from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID
import pandas as pd
from io import BytesIO

from models.database import get_db
from models.models import LocationData
from models.schemas import (
    LocationData as LocationDataSchema,
    LocationDataCreate,
    LocationDataUpdate,
    BaseResponse,
    PaginationParams,
    PaginatedResponse,
    FileUploadResponse
)
from api.auth import verify_token
from geoalchemy2.elements import WKTElement

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_location_data(
    pagination: PaginationParams = Depends(),
    sido: Optional[str] = None,
    sigungu: Optional[str] = None,
    min_population: Optional[int] = None,
    max_rent_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """지역 데이터 목록 조회"""
    query = db.query(LocationData)
    
    # 필터링
    if sido:
        query = query.filter(LocationData.sido == sido)
    if sigungu:
        query = query.filter(LocationData.sigungu == sigungu)
    if min_population:
        query = query.filter(LocationData.population_total >= min_population)
    if max_rent_price:
        query = query.filter(LocationData.rent_price <= max_rent_price)
    
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

@router.get("/{location_id}", response_model=LocationDataSchema)
async def get_location_data_detail(
    location_id: UUID,
    db: Session = Depends(get_db)
):
    """지역 데이터 상세 조회"""
    location_data = db.query(LocationData).filter(LocationData.id == location_id).first()
    if not location_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지역 데이터를 찾을 수 없습니다"
        )
    return location_data

@router.post("/", response_model=LocationDataSchema)
async def create_location_data(
    location_data: LocationDataCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """지역 데이터 생성"""
    db_location_data = LocationData(
        name=location_data.name,
        address=location_data.address,
        sido=location_data.sido,
        sigungu=location_data.sigungu,
        dong=location_data.dong,
        population_total=location_data.population_total,
        population_20s=location_data.population_20s,
        population_30s=location_data.population_30s,
        population_40s=location_data.population_40s,
        population_50s=location_data.population_50s,
        floating_population=location_data.floating_population,
        business_density=location_data.business_density,
        rent_price=location_data.rent_price,
        vacancy_rate=location_data.vacancy_rate,
        competitor_count=location_data.competitor_count,
        similar_business_count=location_data.similar_business_count,
        commercial_area_ratio=location_data.commercial_area_ratio,
        residential_area_ratio=location_data.residential_area_ratio,
        transportation_score=location_data.transportation_score,
        parking_availability_score=location_data.parking_availability_score
    )
    
    # 위치 정보 설정
    if location_data.location:
        db_location_data.location = WKTElement(
            f'POINT({location_data.location.longitude} {location_data.location.latitude})',
            srid=4326
        )
    
    db.add(db_location_data)
    db.commit()
    db.refresh(db_location_data)
    
    return db_location_data

@router.post("/upload", response_model=FileUploadResponse)
async def upload_location_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """지역 데이터 CSV 업로드"""
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
        required_columns = ['name', 'address', 'sido', 'sigungu']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"필수 컬럼 '{col}'이 없습니다"
                )
        
        # 데이터 삽입
        records_processed = 0
        for _, row in df.iterrows():
            location_data = LocationData(
                name=row['name'],
                address=row['address'],
                sido=row['sido'],
                sigungu=row['sigungu'],
                dong=row.get('dong'),
                population_total=row.get('population_total'),
                population_20s=row.get('population_20s'),
                population_30s=row.get('population_30s'),
                population_40s=row.get('population_40s'),
                population_50s=row.get('population_50s'),
                floating_population=row.get('floating_population'),
                business_density=row.get('business_density'),
                rent_price=row.get('rent_price'),
                vacancy_rate=row.get('vacancy_rate'),
                competitor_count=row.get('competitor_count'),
                similar_business_count=row.get('similar_business_count'),
                commercial_area_ratio=row.get('commercial_area_ratio'),
                residential_area_ratio=row.get('residential_area_ratio'),
                transportation_score=row.get('transportation_score'),
                parking_availability_score=row.get('parking_availability_score')
            )
            
            # 위치 정보 설정 (위도, 경도가 있는 경우)
            if 'latitude' in row and 'longitude' in row:
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    location_data.location = WKTElement(
                        f'POINT({row["longitude"]} {row["latitude"]})',
                        srid=4326
                    )
            
            db.add(location_data)
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
async def get_location_data_stats(
    db: Session = Depends(get_db)
):
    """지역 데이터 통계 요약"""
    total_count = db.query(LocationData).count()
    
    # 시도별 통계
    sido_stats = db.query(
        LocationData.sido,
        func.count(LocationData.id).label('count'),
        func.avg(LocationData.population_total).label('avg_population'),
        func.avg(LocationData.rent_price).label('avg_rent_price')
    ).group_by(LocationData.sido).all()
    
    # 전체 평균
    avg_population = db.query(func.avg(LocationData.population_total)).scalar()
    avg_rent_price = db.query(func.avg(LocationData.rent_price)).scalar()
    
    return {
        "total_count": total_count,
        "avg_population": float(avg_population) if avg_population else 0,
        "avg_rent_price": float(avg_rent_price) if avg_rent_price else 0,
        "sido_stats": [
            {
                "sido": stat.sido,
                "count": stat.count,
                "avg_population": float(stat.avg_population) if stat.avg_population else 0,
                "avg_rent_price": float(stat.avg_rent_price) if stat.avg_rent_price else 0
            }
            for stat in sido_stats
        ]
    }

@router.get("/search/nearby")
async def search_nearby_locations(
    latitude: float,
    longitude: float,
    radius: float = 1000,  # 미터 단위
    db: Session = Depends(get_db)
):
    """주변 지역 검색"""
    # PostGIS ST_DWithin 함수를 사용하여 반경 내 지역 검색
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM location_data 
        WHERE ST_DWithin(
            location::geometry, 
            ST_GeogFromText('POINT(' || :longitude || ' ' || :latitude || ')')::geometry, 
            :radius
        )
        ORDER BY ST_Distance(location::geometry, ST_GeogFromText('POINT(' || :longitude || ' ' || :latitude || ')')::geometry)
        LIMIT 20
    """)
    
    result = db.execute(query, {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius
    })
    
    return [dict(row) for row in result]