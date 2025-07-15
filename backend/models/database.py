from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import asyncio
from typing import Generator
from config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# Redis 연결
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# 데이터베이스 세션 의존성
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis 의존성
def get_redis():
    return redis_client

# 데이터베이스 테이블 생성
def create_tables():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 초기화
def init_db():
    # 테이블 생성
    create_tables()
    
    # 기본 데이터 삽입 (필요한 경우)
    pass