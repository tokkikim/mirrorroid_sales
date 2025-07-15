import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional, Any
from decimal import Decimal
import time
from datetime import datetime

from models.models import ReferenceArea, LocationData, AnalysisCondition

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_similarity(
        self,
        reference_area: ReferenceArea,
        analysis_condition: AnalysisCondition,
        custom_weights: Optional[Dict[str, float]] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """기준 상권과 유사한 지역을 분석하여 추천"""
        start_time = time.time()
        
        # 가중치 설정
        weights = self._get_weights(analysis_condition, custom_weights)
        
        # 기준 상권 데이터 정규화
        reference_features = self._extract_features(reference_area)
        
        # 후보 지역 조회
        candidate_locations = self._get_candidate_locations(analysis_condition)
        
        # 유사도 계산
        similarities = []
        for location in candidate_locations:
            location_features = self._extract_features(location)
            similarity_score = self._calculate_similarity(
                reference_features, location_features, weights
            )
            
            if similarity_score > 0.5:  # 최소 유사도 임계값
                similarities.append({
                    'location_id': location.id,
                    'location': location,
                    'similarity_score': similarity_score,
                    'reason': self._generate_reason(reference_features, location_features, weights)
                })
        
        # 유사도 기준 정렬
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # 상위 요인 분석
        top_factors = self._analyze_top_factors(weights)
        
        analysis_duration = time.time() - start_time
        
        return {
            'candidates': similarities,
            'weights': weights,
            'total_candidates': len(candidate_locations),
            'duration': analysis_duration,
            'top_factors': top_factors
        }
    
    def _get_weights(
        self,
        analysis_condition: AnalysisCondition,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """가중치 조회 및 설정"""
        if custom_weights:
            return custom_weights
        
        return {
            'population': float(analysis_condition.weight_population),
            'business_density': float(analysis_condition.weight_business_density),
            'rent_price': float(analysis_condition.weight_rent_price),
            'competition': float(analysis_condition.weight_competition),
            'transportation': float(analysis_condition.weight_transportation)
        }
    
    def _extract_features(self, area) -> Dict[str, float]:
        """지역 특성 추출 및 정규화"""
        features = {
            'population': self._normalize_value(area.population_density or 0, 0, 50000),
            'business_density': self._normalize_value(area.business_density or 0, 0, 100),
            'rent_price': self._normalize_value(area.rent_price or 0, 0, 5000000, inverse=True),
            'competition': self._normalize_value(area.competitor_count or 0, 0, 20, inverse=True),
            'transportation': self._normalize_value(area.transportation_score or 0, 0, 100)
        }
        
        # LocationData 객체인 경우 추가 특성 추출
        if hasattr(area, 'floating_population'):
            features['floating_population'] = self._normalize_value(
                area.floating_population or 0, 0, 100000
            )
        
        return features
    
    def _normalize_value(self, value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
        """값 정규화 (0~1 사이)"""
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0, min(1, normalized))
        
        return 1 - normalized if inverse else normalized
    
    def _get_candidate_locations(self, analysis_condition: AnalysisCondition) -> List[LocationData]:
        """후보 지역 조회"""
        query = self.db.query(LocationData)
        
        # 필터링 조건 적용
        if analysis_condition.min_population:
            query = query.filter(LocationData.population_total >= analysis_condition.min_population)
        
        if analysis_condition.max_rent_price:
            query = query.filter(LocationData.rent_price <= analysis_condition.max_rent_price)
        
        if analysis_condition.max_competitor_count:
            query = query.filter(LocationData.competitor_count <= analysis_condition.max_competitor_count)
        
        return query.all()
    
    def _calculate_similarity(
        self,
        reference_features: Dict[str, float],
        location_features: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """가중 유사도 계산"""
        similarity_score = 0.0
        
        # 공통 특성에 대해 유사도 계산
        common_features = set(reference_features.keys()) & set(location_features.keys())
        
        for feature in common_features:
            if feature in weights:
                # 유클리드 거리 기반 유사도 (0~1 사이)
                distance = abs(reference_features[feature] - location_features[feature])
                feature_similarity = 1 - distance
                similarity_score += feature_similarity * weights[feature]
        
        return min(1.0, max(0.0, similarity_score))
    
    def _generate_reason(
        self,
        reference_features: Dict[str, float],
        location_features: Dict[str, float],
        weights: Dict[str, float]
    ) -> str:
        """추천 사유 생성"""
        reasons = []
        
        # 각 특성별 유사도 분석
        for feature, weight in weights.items():
            if feature in reference_features and feature in location_features:
                ref_val = reference_features[feature]
                loc_val = location_features[feature]
                similarity = 1 - abs(ref_val - loc_val)
                
                if similarity > 0.8 and weight > 0.15:
                    feature_name = self._get_feature_name(feature)
                    reasons.append(f"{feature_name} 유사도 높음")
        
        if not reasons:
            reasons.append("전반적인 지역 특성 유사")
        
        return ", ".join(reasons)
    
    def _get_feature_name(self, feature: str) -> str:
        """특성명 한글 변환"""
        feature_names = {
            'population': '인구밀도',
            'business_density': '업종밀도',
            'rent_price': '임대료',
            'competition': '경쟁강도',
            'transportation': '교통접근성'
        }
        return feature_names.get(feature, feature)
    
    def _analyze_top_factors(self, weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """상위 영향 요인 분석"""
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        top_factors = []
        for feature, weight in sorted_weights[:3]:
            top_factors.append({
                'factor': self._get_feature_name(feature),
                'weight': weight,
                'impact': 'high' if weight > 0.25 else 'medium' if weight > 0.15 else 'low'
            })
        
        return top_factors
    
    async def get_analysis_insights(
        self,
        reference_area_id: str,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """분석 인사이트 생성"""
        if not recommendations:
            return {"insights": []}
        
        insights = []
        
        # 평균 유사도 분석
        avg_similarity = np.mean([r['similarity_score'] for r in recommendations])
        if avg_similarity > 0.8:
            insights.append({
                'type': 'positive',
                'message': '높은 유사도를 가진 지역들이 다수 발견되었습니다.'
            })
        elif avg_similarity < 0.6:
            insights.append({
                'type': 'warning',
                'message': '유사도가 낮은 지역들이 많습니다. 조건을 재검토해보세요.'
            })
        
        # 지역 분포 분석
        region_distribution = {}
        for rec in recommendations:
            location = rec['location']
            region = location.sido
            region_distribution[region] = region_distribution.get(region, 0) + 1
        
        if region_distribution:
            top_region = max(region_distribution, key=region_distribution.get)
            insights.append({
                'type': 'info',
                'message': f'{top_region} 지역에 추천 지역이 집중되어 있습니다.'
            })
        
        return {"insights": insights}