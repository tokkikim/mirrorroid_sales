from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from config import settings
from models.database import engine, Base
from api import reference_areas, location_data, recommendations, analysis, reports, auth

# 애플리케이션 시작시 실행될 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작시 실행
    print("🚀 미라트 스튜디오 가맹 추천 시스템 시작")
    
    # 업로드 및 리포트 폴더 생성
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.REPORT_FOLDER, exist_ok=True)
    
    yield
    
    # 종료시 실행
    print("🛑 미라트 스튜디오 가맹 추천 시스템 종료")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="미라트 스튜디오 가맹점 확장을 위한 데이터 기반 지역 추천 시스템",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory=settings.REPORT_FOLDER), name="reports")

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(reference_areas.router, prefix="/api/reference-areas", tags=["기준 상권"])
app.include_router(location_data.router, prefix="/api/location-data", tags=["지역 데이터"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["추천 결과"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["분석"])
app.include_router(reports.router, prefix="/api/reports", tags=["보고서"])

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "미라트 스튜디오 가맹 추천 지역 분석 시스템",
        "version": settings.VERSION,
        "status": "running"
    }

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API 정보 엔드포인트
@app.get("/api/info")
async def api_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "미라트 스튜디오 가맹점 확장을 위한 데이터 기반 지역 추천 시스템",
        "endpoints": {
            "auth": "/api/auth",
            "reference_areas": "/api/reference-areas",
            "location_data": "/api/location-data",
            "recommendations": "/api/recommendations",
            "analysis": "/api/analysis",
            "reports": "/api/reports"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )