from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import asyncio

from models.database import get_db
from models.models import (
    ReferenceArea, LocationData, RecommendationResult, 
    AnalysisCondition, DataCollectionLog
)
from models.schemas import (
    AnalysisRequest, AnalysisResponse, AnalysisCondition as AnalysisConditionSchema,
    AnalysisConditionCreate, AnalysisConditionUpdate, BaseResponse,
    PaginationParams, PaginatedResponse
)
from api.auth import verify_token
from services.analysis_service import AnalysisService
from services.recommendation_service import RecommendationService

router = APIRouter()

@router.post("/run", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """분석 실행"""
    # 기준 상권 확인
    reference_area = db.query(ReferenceArea).filter(
        ReferenceArea.id == request.reference_area_id
    ).first()
    if not reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    # 분석 조건 확인
    analysis_condition = None
    if request.analysis_condition_id:
        analysis_condition = db.query(AnalysisCondition).filter(
            AnalysisCondition.id == request.analysis_condition_id
        ).first()
        if not analysis_condition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="분석 조건을 찾을 수 없습니다"
            )
    else:
        # 기본 분석 조건 사용
        analysis_condition = db.query(AnalysisCondition).filter(
            AnalysisCondition.is_active == True
        ).first()
    
    # 분석 서비스 실행
    analysis_service = AnalysisService(db)
    recommendation_service = RecommendationService(db)
    
    try:
        # 분석 실행
        analysis_results = await analysis_service.analyze_similarity(
            reference_area=reference_area,
            analysis_condition=analysis_condition,
            custom_weights=request.custom_weights,
            max_results=request.max_results
        )
        
        # 추천 결과 저장
        recommendations = []
        for i, result in enumerate(analysis_results['candidates'][:request.max_results]):
            recommendation = await recommendation_service.create_recommendation(
                reference_area_id=request.reference_area_id,
                recommended_location_id=result['location_id'],
                similarity_score=result['similarity_score'],
                recommendation_reason=result['reason'],
                priority_rank=i + 1,
                created_by=current_user
            )
            recommendations.append(recommendation)
        
        # 분석 요약 생성
        analysis_summary = {
            "analysis_method": "weighted_similarity",
            "weights_used": analysis_results['weights'],
            "total_candidates_analyzed": analysis_results['total_candidates'],
            "analysis_duration": analysis_results['duration'],
            "top_factors": analysis_results['top_factors']
        }
        
        return AnalysisResponse(
            reference_area=reference_area,
            recommendations=recommendations,
            analysis_summary=analysis_summary,
            total_candidates=analysis_results['total_candidates'],
            analysis_time=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 실행 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/conditions", response_model=PaginatedResponse)
async def get_analysis_conditions(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """분석 조건 목록 조회"""
    query = db.query(AnalysisCondition)
    
    if is_active is not None:
        query = query.filter(AnalysisCondition.is_active == is_active)
    
    total = query.count()
    offset = (pagination.page - 1) * pagination.size
    items = query.offset(offset).limit(pagination.size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )

@router.post("/conditions", response_model=AnalysisConditionSchema)
async def create_analysis_condition(
    condition: AnalysisConditionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """분석 조건 생성"""
    # 가중치 합계 검증
    total_weight = (
        condition.weight_population + 
        condition.weight_business_density + 
        condition.weight_rent_price + 
        condition.weight_competition + 
        condition.weight_transportation
    )
    
    if abs(total_weight - 1.0) > 0.001:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="가중치의 합계는 1.0이어야 합니다"
        )
    
    db_condition = AnalysisCondition(
        name=condition.name,
        description=condition.description,
        weight_population=condition.weight_population,
        weight_business_density=condition.weight_business_density,
        weight_rent_price=condition.weight_rent_price,
        weight_competition=condition.weight_competition,
        weight_transportation=condition.weight_transportation,
        min_population=condition.min_population,
        max_rent_price=condition.max_rent_price,
        max_competitor_count=condition.max_competitor_count
    )
    
    db.add(db_condition)
    db.commit()
    db.refresh(db_condition)
    
    return db_condition

@router.put("/conditions/{condition_id}", response_model=AnalysisConditionSchema)
async def update_analysis_condition(
    condition_id: UUID,
    condition: AnalysisConditionUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """분석 조건 수정"""
    db_condition = db.query(AnalysisCondition).filter(
        AnalysisCondition.id == condition_id
    ).first()
    
    if not db_condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="분석 조건을 찾을 수 없습니다"
        )
    
    update_data = condition.dict(exclude_unset=True)
    
    # 가중치 합계 검증 (가중치가 수정되는 경우)
    weights = [
        update_data.get('weight_population', db_condition.weight_population),
        update_data.get('weight_business_density', db_condition.weight_business_density),
        update_data.get('weight_rent_price', db_condition.weight_rent_price),
        update_data.get('weight_competition', db_condition.weight_competition),
        update_data.get('weight_transportation', db_condition.weight_transportation)
    ]
    
    if abs(sum(weights) - 1.0) > 0.001:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="가중치의 합계는 1.0이어야 합니다"
        )
    
    for key, value in update_data.items():
        setattr(db_condition, key, value)
    
    db_condition.updated_at = func.now()
    db.commit()
    db.refresh(db_condition)
    
    return db_condition

@router.get("/history")
async def get_analysis_history(
    pagination: PaginationParams = Depends(),
    reference_area_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """분석 히스토리 조회"""
    query = db.query(RecommendationResult).options(
        joinedload(RecommendationResult.reference_area),
        joinedload(RecommendationResult.recommended_location)
    )
    
    if reference_area_id:
        query = query.filter(RecommendationResult.reference_area_id == reference_area_id)
    
    query = query.order_by(RecommendationResult.analysis_date.desc())
    
    total = query.count()
    offset = (pagination.page - 1) * pagination.size
    items = query.offset(offset).limit(pagination.size).all()
    
    # 분석 히스토리 그룹화
    analysis_history = {}
    for item in items:
        analysis_date = item.analysis_date.date()
        if analysis_date not in analysis_history:
            analysis_history[analysis_date] = []
        analysis_history[analysis_date].append(item)
    
    return {
        "history": analysis_history,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": (total + pagination.size - 1) // pagination.size
    }

@router.get("/status")
async def get_analysis_status(
    db: Session = Depends(get_db)
):
    """분석 상태 조회"""
    # 최근 분석 결과 통계
    recent_analyses = db.query(RecommendationResult).filter(
        RecommendationResult.analysis_date >= func.date_sub(func.now(), interval=30, unit='day')
    ).count()
    
    # 데이터 수집 상태
    data_collection_status = db.query(DataCollectionLog).filter(
        DataCollectionLog.created_at >= func.date_sub(func.now(), interval=7, unit='day')
    ).order_by(DataCollectionLog.created_at.desc()).limit(10).all()
    
    # 활성 분석 조건 수
    active_conditions = db.query(AnalysisCondition).filter(
        AnalysisCondition.is_active == True
    ).count()
    
    return {
        "recent_analyses_count": recent_analyses,
        "active_conditions_count": active_conditions,
        "data_collection_status": data_collection_status,
        "system_status": "healthy"
    }