from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# 기본 스키마 클래스들
class LocationPoint(BaseModel):
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")

class BaseResponse(BaseModel):
    message: str
    status: str = "success"

# 기준 상권 스키마
class ReferenceAreaBase(BaseModel):
    name: str = Field(..., description="상권명")
    address: str = Field(..., description="주소")
    location: Optional[LocationPoint] = None
    monthly_sales: Optional[Decimal] = Field(None, description="월 매출")
    area_type: Optional[str] = Field(None, description="상권 유형")
    population_density: Optional[int] = Field(None, description="인구 밀도")
    competitor_count: Optional[int] = Field(None, description="경쟁업체 수")
    rent_price: Optional[Decimal] = Field(None, description="임대료")
    floor_area: Optional[Decimal] = Field(None, description="면적")

class ReferenceAreaCreate(ReferenceAreaBase):
    pass

class ReferenceAreaUpdate(ReferenceAreaBase):
    name: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class ReferenceArea(ReferenceAreaBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 지역 데이터 스키마
class LocationDataBase(BaseModel):
    name: str = Field(..., description="지역명")
    address: str = Field(..., description="주소")
    location: Optional[LocationPoint] = None
    sido: Optional[str] = Field(None, description="시도")
    sigungu: Optional[str] = Field(None, description="시군구")
    dong: Optional[str] = Field(None, description="동")
    population_total: Optional[int] = Field(None, description="총 인구")
    population_20s: Optional[int] = Field(None, description="20대 인구")
    population_30s: Optional[int] = Field(None, description="30대 인구")
    population_40s: Optional[int] = Field(None, description="40대 인구")
    population_50s: Optional[int] = Field(None, description="50대 인구")
    floating_population: Optional[int] = Field(None, description="유동인구")
    business_density: Optional[Decimal] = Field(None, description="업종 밀도")
    rent_price: Optional[Decimal] = Field(None, description="임대료")
    vacancy_rate: Optional[Decimal] = Field(None, description="공실률")
    competitor_count: Optional[int] = Field(None, description="경쟁업체 수")
    similar_business_count: Optional[int] = Field(None, description="유사업종 수")
    commercial_area_ratio: Optional[Decimal] = Field(None, description="상업지역 비율")
    residential_area_ratio: Optional[Decimal] = Field(None, description="주거지역 비율")
    transportation_score: Optional[int] = Field(None, description="교통 점수")
    parking_availability_score: Optional[int] = Field(None, description="주차 가능성 점수")

class LocationDataCreate(LocationDataBase):
    pass

class LocationDataUpdate(LocationDataBase):
    name: Optional[str] = None
    address: Optional[str] = None

class LocationData(LocationDataBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 추천 결과 스키마
class RecommendationResultBase(BaseModel):
    reference_area_id: UUID
    recommended_location_id: UUID
    similarity_score: Decimal = Field(..., description="유사도 점수")
    recommendation_reason: Optional[str] = Field(None, description="추천 사유")
    priority_rank: Optional[int] = Field(None, description="우선순위")
    created_by: Optional[str] = Field(None, description="생성자")
    is_reviewed: bool = False
    review_comments: Optional[str] = Field(None, description="검토 의견")

class RecommendationResultCreate(RecommendationResultBase):
    pass

class RecommendationResult(RecommendationResultBase):
    id: UUID
    analysis_date: datetime
    reference_area: Optional[ReferenceArea] = None
    recommended_location: Optional[LocationData] = None
    
    class Config:
        from_attributes = True

# 분석 조건 스키마
class AnalysisConditionBase(BaseModel):
    name: str = Field(..., description="조건명")
    description: Optional[str] = Field(None, description="설명")
    weight_population: Decimal = Field(0.25, description="인구 가중치")
    weight_business_density: Decimal = Field(0.25, description="업종 밀도 가중치")
    weight_rent_price: Decimal = Field(0.20, description="임대료 가중치")
    weight_competition: Decimal = Field(0.15, description="경쟁 가중치")
    weight_transportation: Decimal = Field(0.15, description="교통 가중치")
    min_population: int = Field(10000, description="최소 인구")
    max_rent_price: Decimal = Field(1000000, description="최대 임대료")
    max_competitor_count: int = Field(10, description="최대 경쟁업체 수")

class AnalysisConditionCreate(AnalysisConditionBase):
    pass

class AnalysisConditionUpdate(AnalysisConditionBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class AnalysisCondition(AnalysisConditionBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 분석 요청 스키마
class AnalysisRequest(BaseModel):
    reference_area_id: UUID
    analysis_condition_id: Optional[UUID] = None
    custom_weights: Optional[Dict[str, float]] = None
    max_results: int = Field(10, description="최대 결과 수")

class AnalysisResponse(BaseModel):
    reference_area: ReferenceArea
    recommendations: List[RecommendationResult]
    analysis_summary: Dict[str, Any]
    total_candidates: int
    analysis_time: datetime

# 데이터 수집 로그 스키마
class DataCollectionLogBase(BaseModel):
    data_source: str = Field(..., description="데이터 소스")
    collection_type: str = Field(..., description="수집 유형")
    status: str = Field(..., description="상태")
    records_collected: Optional[int] = Field(None, description="수집된 레코드 수")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DataCollectionLog(DataCollectionLogBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# 보고서 스키마
class ReportRequest(BaseModel):
    reference_area_id: UUID
    format: str = Field("excel", description="보고서 형식 (excel, pdf)")
    include_charts: bool = Field(True, description="차트 포함 여부")
    include_details: bool = Field(True, description="상세정보 포함 여부")

class ReportResponse(BaseModel):
    file_path: str
    file_name: str
    generated_at: datetime
    file_size: int

# 업로드 스키마
class FileUploadResponse(BaseModel):
    file_name: str
    file_path: str
    uploaded_at: datetime
    records_processed: int

# 페이지네이션 스키마
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int