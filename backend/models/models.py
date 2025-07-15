from sqlalchemy import Column, String, Integer, Decimal, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import uuid

from .database import Base

class ReferenceArea(Base):
    __tablename__ = "reference_areas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    location = Column(Geography('POINT', srid=4326))
    monthly_sales = Column(Decimal(15, 2))
    area_type = Column(String(50))
    population_density = Column(Integer)
    competitor_count = Column(Integer)
    rent_price = Column(Decimal(10, 2))
    floor_area = Column(Decimal(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 관계 설정
    recommendations = relationship("RecommendationResult", back_populates="reference_area")

class LocationData(Base):
    __tablename__ = "location_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    location = Column(Geography('POINT', srid=4326))
    sido = Column(String(50))
    sigungu = Column(String(50))
    dong = Column(String(50))
    population_total = Column(Integer)
    population_20s = Column(Integer)
    population_30s = Column(Integer)
    population_40s = Column(Integer)
    population_50s = Column(Integer)
    floating_population = Column(Integer)
    business_density = Column(Decimal(10, 2))
    rent_price = Column(Decimal(10, 2))
    vacancy_rate = Column(Decimal(5, 2))
    competitor_count = Column(Integer)
    similar_business_count = Column(Integer)
    commercial_area_ratio = Column(Decimal(5, 2))
    residential_area_ratio = Column(Decimal(5, 2))
    transportation_score = Column(Integer)
    parking_availability_score = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 관계 설정
    business_distributions = relationship("BusinessDistribution", back_populates="location")
    consumer_patterns = relationship("ConsumerPattern", back_populates="location")
    recommendations = relationship("RecommendationResult", back_populates="recommended_location")

class BusinessDistribution(Base):
    __tablename__ = "business_distribution"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("location_data.id"))
    business_type = Column(String(100))
    business_count = Column(Integer)
    total_sales = Column(Decimal(15, 2))
    avg_sales = Column(Decimal(15, 2))
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    location = relationship("LocationData", back_populates="business_distributions")

class ConsumerPattern(Base):
    __tablename__ = "consumer_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("location_data.id"))
    age_group = Column(String(20))
    gender = Column(String(10))
    spending_amount = Column(Decimal(12, 2))
    spending_frequency = Column(Integer)
    preferred_time_slot = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    location = relationship("LocationData", back_populates="consumer_patterns")

class RecommendationResult(Base):
    __tablename__ = "recommendation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_area_id = Column(UUID(as_uuid=True), ForeignKey("reference_areas.id"))
    recommended_location_id = Column(UUID(as_uuid=True), ForeignKey("location_data.id"))
    similarity_score = Column(Decimal(5, 4))
    recommendation_reason = Column(Text)
    priority_rank = Column(Integer)
    analysis_date = Column(DateTime, default=func.now())
    created_by = Column(String(100))
    is_reviewed = Column(Boolean, default=False)
    review_comments = Column(Text)
    
    # 관계 설정
    reference_area = relationship("ReferenceArea", back_populates="recommendations")
    recommended_location = relationship("LocationData", back_populates="recommendations")

class AnalysisCondition(Base):
    __tablename__ = "analysis_conditions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    weight_population = Column(Decimal(3, 2), default=0.25)
    weight_business_density = Column(Decimal(3, 2), default=0.25)
    weight_rent_price = Column(Decimal(3, 2), default=0.20)
    weight_competition = Column(Decimal(3, 2), default=0.15)
    weight_transportation = Column(Decimal(3, 2), default=0.15)
    min_population = Column(Integer, default=10000)
    max_rent_price = Column(Decimal(10, 2), default=1000000)
    max_competitor_count = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class DataCollectionLog(Base):
    __tablename__ = "data_collection_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source = Column(String(100))
    collection_type = Column(String(50))
    status = Column(String(20))
    records_collected = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())