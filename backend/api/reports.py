from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import os
import asyncio

from models.database import get_db
from models.models import ReferenceArea, RecommendationResult, LocationData
from models.schemas import (
    ReportRequest, ReportResponse, BaseResponse
)
from api.auth import verify_token
from services.report_service import ReportService
from config import settings

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 생성"""
    # 기준 상권 확인
    reference_area = db.query(ReferenceArea).filter(
        ReferenceArea.id == request.reference_area_id
    ).first()
    if not reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    # 추천 결과 조회
    recommendations = db.query(RecommendationResult).options(
        joinedload(RecommendationResult.recommended_location)
    ).filter(
        RecommendationResult.reference_area_id == request.reference_area_id
    ).order_by(RecommendationResult.similarity_score.desc()).all()
    
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천 결과가 없습니다. 먼저 분석을 실행해주세요."
        )
    
    # 보고서 서비스 실행
    report_service = ReportService(db)
    
    try:
        if request.format.lower() == "excel":
            file_path = await report_service.generate_excel_report(
                reference_area=reference_area,
                recommendations=recommendations,
                include_charts=request.include_charts,
                include_details=request.include_details
            )
        elif request.format.lower() == "pdf":
            file_path = await report_service.generate_pdf_report(
                reference_area=reference_area,
                recommendations=recommendations,
                include_charts=request.include_charts,
                include_details=request.include_details
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 보고서 형식입니다. (excel, pdf만 지원)"
            )
        
        # 파일 정보 반환
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        return ReportResponse(
            file_path=file_path,
            file_name=file_name,
            generated_at=datetime.now(),
            file_size=file_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/download/{file_name}")
async def download_report(
    file_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 다운로드"""
    file_path = os.path.join(settings.REPORT_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보고서 파일을 찾을 수 없습니다"
        )
    
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/octet-stream'
    )

@router.get("/list")
async def list_reports(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 목록 조회"""
    reports_dir = settings.REPORT_FOLDER
    
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    reports = []
    for file_name in os.listdir(reports_dir):
        if file_name.endswith(('.xlsx', '.pdf')):
            file_path = os.path.join(reports_dir, file_name)
            file_stat = os.stat(file_path)
            
            reports.append({
                "file_name": file_name,
                "file_size": file_stat.st_size,
                "created_at": datetime.fromtimestamp(file_stat.st_ctime),
                "modified_at": datetime.fromtimestamp(file_stat.st_mtime)
            })
    
    # 생성일시 내림차순 정렬
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {"reports": reports}

@router.delete("/delete/{file_name}", response_model=BaseResponse)
async def delete_report(
    file_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 삭제"""
    file_path = os.path.join(settings.REPORT_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보고서 파일을 찾을 수 없습니다"
        )
    
    try:
        os.remove(file_path)
        return BaseResponse(
            message="보고서가 삭제되었습니다",
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/template/create")
async def create_report_template(
    template_name: str,
    reference_area_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 템플릿 생성"""
    # 기준 상권 확인
    reference_area = db.query(ReferenceArea).filter(
        ReferenceArea.id == reference_area_id
    ).first()
    if not reference_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기준 상권을 찾을 수 없습니다"
        )
    
    # 템플릿 생성 로직 (구현 예정)
    return BaseResponse(
        message="보고서 템플릿이 생성되었습니다",
        status="success"
    )

@router.get("/templates")
async def get_report_templates(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """보고서 템플릿 목록 조회"""
    # 템플릿 목록 조회 로직 (구현 예정)
    return {"templates": []}

@router.get("/analytics/summary")
async def get_report_analytics(
    db: Session = Depends(get_db)
):
    """보고서 생성 통계"""
    reports_dir = settings.REPORT_FOLDER
    
    if not os.path.exists(reports_dir):
        return {
            "total_reports": 0,
            "excel_reports": 0,
            "pdf_reports": 0,
            "total_size": 0
        }
    
    total_reports = 0
    excel_reports = 0
    pdf_reports = 0
    total_size = 0
    
    for file_name in os.listdir(reports_dir):
        if file_name.endswith('.xlsx'):
            excel_reports += 1
            total_reports += 1
        elif file_name.endswith('.pdf'):
            pdf_reports += 1
            total_reports += 1
        
        if file_name.endswith(('.xlsx', '.pdf')):
            file_path = os.path.join(reports_dir, file_name)
            total_size += os.path.getsize(file_path)
    
    return {
        "total_reports": total_reports,
        "excel_reports": excel_reports,
        "pdf_reports": pdf_reports,
        "total_size": total_size
    }