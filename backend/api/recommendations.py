from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from models.database import get_db
from models.models import RecommendationResult, ReferenceArea, LocationData
from models.schemas import (
    RecommendationResult as RecommendationResultSchema,
    RecommendationResultCreate,
    BaseResponse,
    PaginationParams,
    PaginatedResponse
)
from api.auth import verify_token

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_recommendations(
    pagination: PaginationParams = Depends(),
    reference_area_id: Optional[UUID] = None,
    min_similarity_score: Optional[float] = None,
    is_reviewed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """추천 결과 목록 조회"""
    query = db.query(RecommendationResult).options(
        joinedload(RecommendationResult.reference_area),
        joinedload(RecommendationResult.recommended_location)
    )
    
    # 필터링
    if reference_area_id:
        query = query.filter(RecommendationResult.reference_area_id == reference_area_id)
    if min_similarity_score:
        query = query.filter(RecommendationResult.similarity_score >= min_similarity_score)
    if is_reviewed is not None:
        query = query.filter(RecommendationResult.is_reviewed == is_reviewed)
    
    # 유사도 점수 내림차순 정렬
    query = query.order_by(desc(RecommendationResult.similarity_score))
    
    # 총 개수
    total = query.count()
    
    # 페이지네이션
    offset = (pagination.page - 1) * pagination.size
    items = query.offset(offset).limit(pagination.size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )

@router.get("/{recommendation_id}", response_model=RecommendationResultSchema)
async def get_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db)
):
    """추천 결과 상세 조회"""
    recommendation = db.query(RecommendationResult).options(
        joinedload(RecommendationResult.reference_area),
        joinedload(RecommendationResult.recommended_location)
    ).filter(RecommendationResult.id == recommendation_id).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 결과를 찾을 수 없습니다"
        )
    return recommendation

@router.post("/", response_model=RecommendationResultSchema)
async def create_recommendation(
    recommendation: RecommendationResultCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """추천 결과 생성"""
    # 기준 상권 및 추천 지역 존재 확인
    reference_area = db.query(ReferenceArea).filter(
        ReferenceArea.id == recommendation.reference_area_id
    ).first()
    if not reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    recommended_location = db.query(LocationData).filter(
        LocationData.id == recommendation.recommended_location_id
    ).first()
    if not recommended_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 지역을 찾을 수 없습니다"
        )
    
    # 추천 결과 생성
    db_recommendation = RecommendationResult(
        reference_area_id=recommendation.reference_area_id,
        recommended_location_id=recommendation.recommended_location_id,
        similarity_score=recommendation.similarity_score,
        recommendation_reason=recommendation.recommendation_reason,
        priority_rank=recommendation.priority_rank,
        created_by=current_user,
        is_reviewed=recommendation.is_reviewed,
        review_comments=recommendation.review_comments
    )
    
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    
    return db_recommendation

@router.put("/{recommendation_id}/review", response_model=RecommendationResultSchema)
async def review_recommendation(
    recommendation_id: UUID,
    review_comments: str,
    is_approved: bool,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """추천 결과 검토"""
    recommendation = db.query(RecommendationResult).filter(
        RecommendationResult.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 결과를 찾을 수 없습니다"
        )
    
    recommendation.is_reviewed = True
    recommendation.review_comments = review_comments
    recommendation.created_by = current_user  # 검토자 정보 업데이트
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation

@router.delete("/{recommendation_id}", response_model=BaseResponse)
async def delete_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """추천 결과 삭제"""
    recommendation = db.query(RecommendationResult).filter(
        RecommendationResult.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 결과를 찾을 수 없습니다"
        )
    
    db.delete(recommendation)
    db.commit()
    
    return BaseResponse(
        message="추천 결과가 삭제되었습니다",
        status="success"
    )

@router.get("/reference-area/{reference_area_id}/top")
async def get_top_recommendations_by_reference_area(
    reference_area_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """기준 상권별 상위 추천 결과 조회"""
    recommendations = db.query(RecommendationResult).options(
        joinedload(RecommendationResult.recommended_location)
    ).filter(
        RecommendationResult.reference_area_id == reference_area_id
    ).order_by(
        desc(RecommendationResult.similarity_score)
    ).limit(limit).all()
    
    return recommendations

@router.get("/stats/summary")
async def get_recommendations_stats(
    db: Session = Depends(get_db)
):
    """추천 결과 통계 요약"""
    total_count = db.query(RecommendationResult).count()
    reviewed_count = db.query(RecommendationResult).filter(
        RecommendationResult.is_reviewed == True
    ).count()
    
    # 평균 유사도 점수
    avg_similarity = db.query(func.avg(RecommendationResult.similarity_score)).scalar()
    
    # 기준 상권별 추천 수
    reference_area_stats = db.query(
        ReferenceArea.name,
        func.count(RecommendationResult.id).label('recommendation_count'),
        func.avg(RecommendationResult.similarity_score).label('avg_similarity')
    ).join(
        RecommendationResult, ReferenceArea.id == RecommendationResult.reference_area_id
    ).group_by(ReferenceArea.id, ReferenceArea.name).all()
    
    return {
        "total_count": total_count,
        "reviewed_count": reviewed_count,
        "unreviewed_count": total_count - reviewed_count,
        "avg_similarity_score": float(avg_similarity) if avg_similarity else 0,
        "reference_area_stats": [
            {
                "reference_area_name": stat.name,
                "recommendation_count": stat.recommendation_count,
                "avg_similarity": float(stat.avg_similarity) if stat.avg_similarity else 0
            }
            for stat in reference_area_stats
        ]
    }