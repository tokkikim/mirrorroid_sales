from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
import pandas as pd
from io import BytesIO

from models.database import get_db
from models.models import ReferenceArea
from models.schemas import (
    ReferenceArea as ReferenceAreaSchema,
    ReferenceAreaCreate,
    ReferenceAreaUpdate,
    BaseResponse,
    PaginationParams,
    PaginatedResponse,
    FileUploadResponse
)
from api.auth import verify_token
from geoalchemy2.elements import WKTElement

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_reference_areas(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = None,
    area_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """기준 상권 목록 조회"""
    query = db.query(ReferenceArea)
    
    # 필터링
    if is_active is not None:
        query = query.filter(ReferenceArea.is_active == is_active)
    if area_type:
        query = query.filter(ReferenceArea.area_type == area_type)
    
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

@router.get("/{reference_area_id}", response_model=ReferenceAreaSchema)
async def get_reference_area(
    reference_area_id: UUID,
    db: Session = Depends(get_db)
):
    """기준 상권 상세 조회"""
    reference_area = db.query(ReferenceArea).filter(ReferenceArea.id == reference_area_id).first()
    if not reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    return reference_area

@router.post("/", response_model=ReferenceAreaSchema)
async def create_reference_area(
    reference_area: ReferenceAreaCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """기준 상권 생성"""
    db_reference_area = ReferenceArea(
        name=reference_area.name,
        address=reference_area.address,
        monthly_sales=reference_area.monthly_sales,
        area_type=reference_area.area_type,
        population_density=reference_area.population_density,
        competitor_count=reference_area.competitor_count,
        rent_price=reference_area.rent_price,
        floor_area=reference_area.floor_area
    )
    
    # 위치 정보 설정
    if reference_area.location:
        db_reference_area.location = WKTElement(
            f'POINT({reference_area.location.longitude} {reference_area.location.latitude})',
            srid=4326
        )
    
    db.add(db_reference_area)
    db.commit()
    db.refresh(db_reference_area)
    
    return db_reference_area

@router.put("/{reference_area_id}", response_model=ReferenceAreaSchema)
async def update_reference_area(
    reference_area_id: UUID,
    reference_area: ReferenceAreaUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """기준 상권 수정"""
    db_reference_area = db.query(ReferenceArea).filter(ReferenceArea.id == reference_area_id).first()
    if not db_reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    # 업데이트 필드 설정
    update_data = reference_area.dict(exclude_unset=True)
    
    # 위치 정보 처리
    if 'location' in update_data and update_data['location']:
        location = update_data.pop('location')
        db_reference_area.location = WKTElement(
            f'POINT({location.longitude} {location.latitude})',
            srid=4326
        )
    
    # 나머지 필드 업데이트
    for key, value in update_data.items():
        setattr(db_reference_area, key, value)
    
    db_reference_area.updated_at = func.now()
    db.commit()
    db.refresh(db_reference_area)
    
    return db_reference_area

@router.delete("/{reference_area_id}", response_model=BaseResponse)
async def delete_reference_area(
    reference_area_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """기준 상권 삭제 (비활성화)"""
    db_reference_area = db.query(ReferenceArea).filter(ReferenceArea.id == reference_area_id).first()
    if not db_reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    # 소프트 삭제 (비활성화)
    db_reference_area.is_active = False
    db_reference_area.updated_at = func.now()
    db.commit()
    
    return BaseResponse(
        message="기준 상권이 삭제되었습니다",
        status="success"
    )

@router.post("/upload", response_model=FileUploadResponse)
async def upload_reference_areas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """기준 상권 데이터 CSV 업로드"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV 파일만 업로드 가능합니다"
        )
    
    try:
        # CSV 파일 읽기
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        # 필수 컬럼 확인
        required_columns = ['name', 'address']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"필수 컬럼 '{col}'이 없습니다"
                )
        
        # 데이터 삽입
        records_processed = 0
        for _, row in df.iterrows():
            reference_area = ReferenceArea(
                name=row['name'],
                address=row['address'],
                monthly_sales=row.get('monthly_sales'),
                area_type=row.get('area_type'),
                population_density=row.get('population_density'),
                competitor_count=row.get('competitor_count'),
                rent_price=row.get('rent_price'),
                floor_area=row.get('floor_area')
            )
            
            # 위치 정보 설정 (위도, 경도가 있는 경우)
            if 'latitude' in row and 'longitude' in row:
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    reference_area.location = WKTElement(
                        f'POINT({row["longitude"]} {row["latitude"]})',
                        srid=4326
                    )
            
            db.add(reference_area)
            records_processed += 1
        
        db.commit()
        
        return FileUploadResponse(
            file_name=file.filename,
            file_path=f"uploads/{file.filename}",
            uploaded_at=func.now(),
            records_processed=records_processed
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/stats/summary")
async def get_reference_areas_stats(
    db: Session = Depends(get_db)
):
    """기준 상권 통계 요약"""
    total_count = db.query(ReferenceArea).count()
    active_count = db.query(ReferenceArea).filter(ReferenceArea.is_active == True).count()
    
    # 상권 유형별 통계
    area_types = db.query(
        ReferenceArea.area_type,
        func.count(ReferenceArea.id).label('count')
    ).group_by(ReferenceArea.area_type).all()
    
    # 평균 매출
    avg_sales = db.query(func.avg(ReferenceArea.monthly_sales)).scalar()
    
    return {
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": total_count - active_count,
        "area_types": [{"type": at.area_type, "count": at.count} for at in area_types],
        "avg_monthly_sales": float(avg_sales) if avg_sales else 0
    }