from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from models.models import RecommendationResult, ReferenceArea, LocationData

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_recommendation(
        self,
        reference_area_id: UUID,
        recommended_location_id: UUID,
        similarity_score: float,
        recommendation_reason: str,
        priority_rank: int,
        created_by: str
    ) -> RecommendationResult:
        """추천 결과 생성"""
        recommendation = RecommendationResult(
            reference_area_id=reference_area_id,
            recommended_location_id=recommended_location_id,
            similarity_score=Decimal(str(similarity_score)),
            recommendation_reason=recommendation_reason,
            priority_rank=priority_rank,
            created_by=created_by
        )
        
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        
        return recommendation
    
    async def get_recommendations_by_reference_area(
        self,
        reference_area_id: UUID,
        limit: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[RecommendationResult]:
        """기준 상권별 추천 결과 조회"""
        query = self.db.query(RecommendationResult).filter(
            RecommendationResult.reference_area_id == reference_area_id
        )
        
        if min_similarity:
            query = query.filter(RecommendationResult.similarity_score >= min_similarity)
        
        query = query.order_by(desc(RecommendationResult.similarity_score))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def update_recommendation_review(
        self,
        recommendation_id: UUID,
        is_reviewed: bool,
        review_comments: str,
        reviewed_by: str
    ) -> Optional[RecommendationResult]:
        """추천 결과 검토 업데이트"""
        recommendation = self.db.query(RecommendationResult).filter(
            RecommendationResult.id == recommendation_id
        ).first()
        
        if not recommendation:
            return None
        
        recommendation.is_reviewed = is_reviewed
        recommendation.review_comments = review_comments
        recommendation.created_by = reviewed_by  # 검토자 정보
        
        self.db.commit()
        self.db.refresh(recommendation)
        
        return recommendation
    
    async def get_recommendation_statistics(
        self,
        reference_area_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """추천 결과 통계"""
        query = self.db.query(RecommendationResult)
        
        if reference_area_id:
            query = query.filter(RecommendationResult.reference_area_id == reference_area_id)
        
        total_count = query.count()
        reviewed_count = query.filter(RecommendationResult.is_reviewed == True).count()
        
        # 평균 유사도
        avg_similarity = query.with_entities(
            func.avg(RecommendationResult.similarity_score)
        ).scalar()
        
        # 유사도 분포
        high_similarity = query.filter(RecommendationResult.similarity_score >= 0.8).count()
        medium_similarity = query.filter(
            RecommendationResult.similarity_score >= 0.6,
            RecommendationResult.similarity_score < 0.8
        ).count()
        low_similarity = query.filter(RecommendationResult.similarity_score < 0.6).count()
        
        return {
            'total_count': total_count,
            'reviewed_count': reviewed_count,
            'unreviewed_count': total_count - reviewed_count,
            'avg_similarity': float(avg_similarity) if avg_similarity else 0,
            'similarity_distribution': {
                'high': high_similarity,
                'medium': medium_similarity,
                'low': low_similarity
            }
        }
    
    async def get_top_recommendations_summary(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """상위 추천 결과 요약"""
        recommendations = self.db.query(RecommendationResult).join(
            ReferenceArea, RecommendationResult.reference_area_id == ReferenceArea.id
        ).join(
            LocationData, RecommendationResult.recommended_location_id == LocationData.id
        ).order_by(desc(RecommendationResult.similarity_score)).limit(limit).all()
        
        summary = []
        for rec in recommendations:
            summary.append({
                'recommendation_id': rec.id,
                'reference_area_name': rec.reference_area.name,
                'recommended_location_name': rec.recommended_location.name,
                'similarity_score': float(rec.similarity_score),
                'recommendation_reason': rec.recommendation_reason,
                'analysis_date': rec.analysis_date,
                'is_reviewed': rec.is_reviewed
            })
        
        return summary
    
    async def bulk_update_priorities(
        self,
        reference_area_id: UUID,
        priority_updates: List[Dict[str, Any]]
    ) -> bool:
        """추천 결과 우선순위 일괄 업데이트"""
        try:
            for update in priority_updates:
                recommendation = self.db.query(RecommendationResult).filter(
                    RecommendationResult.id == update['recommendation_id'],
                    RecommendationResult.reference_area_id == reference_area_id
                ).first()
                
                if recommendation:
                    recommendation.priority_rank = update['priority_rank']
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            return False
    
    async def delete_old_recommendations(
        self,
        reference_area_id: UUID,
        keep_latest: int = 50
    ) -> int:
        """오래된 추천 결과 삭제"""
        # 최신 추천 결과 ID 조회
        latest_recommendations = self.db.query(RecommendationResult.id).filter(
            RecommendationResult.reference_area_id == reference_area_id
        ).order_by(desc(RecommendationResult.analysis_date)).limit(keep_latest).all()
        
        latest_ids = [rec.id for rec in latest_recommendations]
        
        # 오래된 추천 결과 삭제
        deleted_count = self.db.query(RecommendationResult).filter(
            RecommendationResult.reference_area_id == reference_area_id,
            ~RecommendationResult.id.in_(latest_ids)
        ).delete(synchronize_session=False)
        
        self.db.commit()
        return deleted_count
    
    async def get_recommendation_trends(
        self,
        reference_area_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """추천 결과 트렌드 분석"""
        # 최근 N일간의 추천 결과 조회
        recent_recommendations = self.db.query(RecommendationResult).filter(
            RecommendationResult.reference_area_id == reference_area_id,
            RecommendationResult.analysis_date >= func.date_sub(func.now(), interval=days, unit='day')
        ).order_by(RecommendationResult.analysis_date).all()
        
        # 일별 추천 수 및 평균 유사도
        daily_stats = {}
        for rec in recent_recommendations:
            date_key = rec.analysis_date.date()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'count': 0,
                    'similarities': []
                }
            daily_stats[date_key]['count'] += 1
            daily_stats[date_key]['similarities'].append(float(rec.similarity_score))
        
        # 평균 유사도 계산
        for date_key, stats in daily_stats.items():
            stats['avg_similarity'] = sum(stats['similarities']) / len(stats['similarities'])
        
        return {
            'period_days': days,
            'daily_stats': daily_stats,
            'total_recommendations': len(recent_recommendations)
        }