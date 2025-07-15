-- 미라트 스튜디오 가맹 추천 지역 분석 시스템 데이터베이스 스키마

-- 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 기준 상권 테이블
CREATE TABLE reference_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    monthly_sales DECIMAL(15,2),
    area_type VARCHAR(50), -- 상권 유형 (번화가, 주택가, 상업지구 등)
    population_density INTEGER,
    competitor_count INTEGER,
    rent_price DECIMAL(10,2),
    floor_area DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 지역 데이터 테이블
CREATE TABLE location_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    sido VARCHAR(50),
    sigungu VARCHAR(50),
    dong VARCHAR(50),
    population_total INTEGER,
    population_20s INTEGER,
    population_30s INTEGER,
    population_40s INTEGER,
    population_50s INTEGER,
    floating_population INTEGER,
    business_density DECIMAL(10,2),
    rent_price DECIMAL(10,2),
    vacancy_rate DECIMAL(5,2),
    competitor_count INTEGER,
    similar_business_count INTEGER,
    commercial_area_ratio DECIMAL(5,2),
    residential_area_ratio DECIMAL(5,2),
    transportation_score INTEGER,
    parking_availability_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 업종 분포 테이블
CREATE TABLE business_distribution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID REFERENCES location_data(id),
    business_type VARCHAR(100),
    business_count INTEGER,
    total_sales DECIMAL(15,2),
    avg_sales DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 소비자 패턴 테이블
CREATE TABLE consumer_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID REFERENCES location_data(id),
    age_group VARCHAR(20),
    gender VARCHAR(10),
    spending_amount DECIMAL(12,2),
    spending_frequency INTEGER,
    preferred_time_slot VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 추천 결과 테이블
CREATE TABLE recommendation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_area_id UUID REFERENCES reference_areas(id),
    recommended_location_id UUID REFERENCES location_data(id),
    similarity_score DECIMAL(5,4),
    recommendation_reason TEXT,
    priority_rank INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    is_reviewed BOOLEAN DEFAULT false,
    review_comments TEXT
);

-- 분석 조건 테이블
CREATE TABLE analysis_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    weight_population DECIMAL(3,2) DEFAULT 0.25,
    weight_business_density DECIMAL(3,2) DEFAULT 0.25,
    weight_rent_price DECIMAL(3,2) DEFAULT 0.20,
    weight_competition DECIMAL(3,2) DEFAULT 0.15,
    weight_transportation DECIMAL(3,2) DEFAULT 0.15,
    min_population INTEGER DEFAULT 10000,
    max_rent_price DECIMAL(10,2) DEFAULT 1000000,
    max_competitor_count INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 데이터 수집 로그 테이블
CREATE TABLE data_collection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_source VARCHAR(100),
    collection_type VARCHAR(50),
    status VARCHAR(20),
    records_collected INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_reference_areas_location ON reference_areas USING GIST (location);
CREATE INDEX idx_location_data_location ON location_data USING GIST (location);
CREATE INDEX idx_location_data_sido_sigungu ON location_data (sido, sigungu);
CREATE INDEX idx_recommendation_results_score ON recommendation_results (similarity_score DESC);
CREATE INDEX idx_recommendation_results_date ON recommendation_results (analysis_date DESC);

-- 기본 분석 조건 데이터 삽입
INSERT INTO analysis_conditions (name, description) VALUES 
('기본 분석 조건', '인구밀도, 업종분포, 임대료, 경쟁업체수, 교통접근성을 고려한 기본 분석 조건');

-- 기준 상권 샘플 데이터 (용리단길, 평택 번화가)
INSERT INTO reference_areas (name, address, location, monthly_sales, area_type, population_density, competitor_count, rent_price, floor_area) VALUES
('용리단길점', '서울특별시 용산구 용리단길', ST_GeogFromText('POINT(126.9925 37.5347)'), 15000000, '번화가', 25000, 3, 2000000, 50.0),
('평택 번화가점', '경기도 평택시 중앙로', ST_GeogFromText('POINT(127.1128 36.9951)'), 12000000, '번화가', 18000, 2, 1500000, 45.0);