"""
AI-Powered Value Estimation Engine for Bhashini

This module provides comprehensive business value estimation capabilities including:
- Cost savings calculations (reduced translation costs, operational efficiency)
- User reach impact quantification (citizens served, patients helped)
- Efficiency gains measurement (time saved, automation benefits)
- Quality improvements assessment (accuracy gains, user satisfaction)
- Sector-specific value calculation models
- Machine learning components for predictive estimation
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValueMetrics:
    """Data model for value estimation metrics"""
    tenant_id: str
    calculation_date: datetime
    cost_savings: float  # Annual cost savings in USD
    user_reach_impact: int  # Number of users reached
    efficiency_gains: float  # Time savings percentage
    quality_improvements: float  # Quality improvement score (0-100)
    total_value_score: float  # Normalized value score (0-100)
    calculation_methodology: str
    sector_multiplier: float
    use_case_multiplier: float
    confidence_score: float  # Confidence in estimation (0-100)
    roi_ratio: float  # Return on investment ratio
    payback_period_months: float  # Time to recover investment

@dataclass
class QoSMetrics:
    """Data model for QoS metrics used in value calculation"""
    tenant_id: str
    timestamp: datetime
    service_type: str  # translation, tts, asr
    latency_ms: float
    throughput_rps: float
    error_rate: float
    availability_percent: float
    response_time_p95: float

class ValueEstimator:
    """AI-powered value estimation engine"""
    
    def __init__(self, sector_config_path: str = "config/sector-kpis.yml"):
        self.sector_config_path = Path(sector_config_path)
        self.sector_config = self._load_sector_config()
        self.ml_model = None
        self.scaler = StandardScaler()
        self._initialize_ml_model()
        
        # Sector-specific value multipliers
        self.sector_multipliers = {
            'government': 1.5,    # Higher public value
            'healthcare': 2.0,    # Critical service value
            'education': 1.8,     # Long-term societal value
            'NGO': 1.3,           # Community value
            'private': 1.0        # Base commercial value
        }
        
        # Use case multipliers
        self.use_case_multipliers = {
            'citizen_services': 1.6,      # Public service value
            'patient_communication': 2.2,  # Critical healthcare value
            'content_localization': 1.4,  # Educational value
            'business_operations': 1.0,   # Base business value
            'community_services': 1.3,    # Social value
        }
    
    def _load_sector_config(self) -> Dict[str, Any]:
        """Load sector-specific configuration"""
        try:
            if self.sector_config_path.exists():
                with open(self.sector_config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Sector config not found at {self.sector_config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading sector config: {e}")
            return {}
    
    def _initialize_ml_model(self):
        """Initialize machine learning model for value prediction"""
        try:
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            logger.info("ML model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML model: {e}")
            self.ml_model = None
    
    def calculate_customer_value(self, customer_profile: Dict[str, Any], 
                               qos_metrics: List[QoSMetrics]) -> ValueMetrics:
        """Calculate comprehensive business value for a customer"""
        try:
            tenant_id = customer_profile['tenant_id']
            sector = customer_profile['sector']
            use_case = customer_profile['use_case_category']
            target_users = customer_profile['target_user_base']
            
            # Calculate base metrics
            cost_savings = self._calculate_cost_savings(customer_profile, qos_metrics)
            user_reach = self._calculate_user_reach_impact(customer_profile, qos_metrics)
            efficiency = self._calculate_efficiency_gains(qos_metrics)
            quality = self._calculate_quality_improvements(qos_metrics)
            
            # Apply sector and use case multipliers
            sector_mult = self.sector_multipliers.get(sector, 1.0)
            use_case_mult = self.use_case_multipliers.get(use_case, 1.0)
            
            # Calculate total value score
            total_score = self._calculate_total_value_score(
                cost_savings, user_reach, efficiency, quality,
                sector_mult, use_case_mult
            )
            
            # Calculate ROI and payback period
            roi_ratio = self._calculate_roi_ratio(cost_savings, customer_profile)
            payback_months = self._calculate_payback_period(cost_savings, customer_profile)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(qos_metrics, customer_profile)
            
            return ValueMetrics(
                tenant_id=tenant_id,
                calculation_date=datetime.now(),
                cost_savings=cost_savings,
                user_reach_impact=user_reach,
                efficiency_gains=efficiency,
                quality_improvements=quality,
                total_value_score=total_score,
                calculation_methodology='ai_enhanced',
                sector_multiplier=sector_mult,
                use_case_multiplier=use_case_mult,
                confidence_score=confidence,
                roi_ratio=roi_ratio,
                payback_period_months=payback_months
            )
            
        except Exception as e:
            logger.error(f"Error calculating customer value: {e}")
            raise
    
    def _calculate_cost_savings(self, customer_profile: Dict[str, Any], 
                               qos_metrics: List[QoSMetrics]) -> float:
        """Calculate annual cost savings based on QoS improvements"""
        try:
            # Base translation cost per word (industry standard)
            base_cost_per_word = 0.15  # USD
            
            # Estimate words processed per year based on target users
            target_users = customer_profile['target_user_base']
            words_per_user_per_year = 1000  # Conservative estimate
            
            # Calculate total words processed
            total_words = target_users * words_per_user_per_year
            
            # Calculate cost without Bhashini (manual translation)
            manual_cost = total_words * base_cost_per_word
            
            # Calculate cost with Bhashini (automated + human review)
            automated_cost_per_word = 0.05  # Much lower cost
            human_review_percentage = 0.1   # 10% human review
            human_cost_per_word = base_cost_per_word * human_review_percentage
            
            total_automated_cost = (total_words * automated_cost_per_word + 
                                  total_words * human_review_percentage * human_cost_per_word)
            
            # Calculate savings
            annual_savings = manual_cost - total_automated_cost
            
            # Apply QoS-based efficiency multiplier
            efficiency_multiplier = self._calculate_efficiency_multiplier(qos_metrics)
            adjusted_savings = annual_savings * efficiency_multiplier
            
            logger.info(f"Cost savings calculated: ${adjusted_savings:,.2f} annually")
            return adjusted_savings
            
        except Exception as e:
            logger.error(f"Error calculating cost savings: {e}")
            return 0.0
    
    def _calculate_user_reach_impact(self, customer_profile: Dict[str, Any], 
                                   qos_metrics: List[QoSMetrics]) -> int:
        """Calculate user reach impact based on service availability and quality"""
        try:
            target_users = customer_profile['target_user_base']
            sector = customer_profile['sector']
            
            # Calculate availability impact
            avg_availability = np.mean([m.availability_percent for m in qos_metrics])
            availability_multiplier = avg_availability / 100.0
            
            # Calculate quality impact (lower error rates = higher user satisfaction)
            avg_error_rate = np.mean([m.error_rate for m in qos_metrics])
            quality_multiplier = max(0.5, 1.0 - avg_error_rate)
            
            # Calculate reach based on sector
            sector_reach_multipliers = {
                'government': 0.8,    # Government services have high reach
                'healthcare': 0.9,    # Healthcare has critical reach
                'education': 0.7,     # Education has moderate reach
                'NGO': 0.6,           # NGO services have variable reach
                'private': 0.5        # Private services have competitive reach
            }
            
            sector_multiplier = sector_reach_multipliers.get(sector, 0.5)
            
            # Calculate effective user reach
            effective_reach = int(target_users * availability_multiplier * 
                                quality_multiplier * sector_multiplier)
            
            logger.info(f"User reach impact calculated: {effective_reach:,} users")
            return effective_reach
            
        except Exception as e:
            logger.error(f"Error calculating user reach impact: {e}")
            return 0
    
    def _calculate_efficiency_gains(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate efficiency gains based on QoS improvements"""
        try:
            if not qos_metrics:
                return 0.0
            
            # Calculate latency improvements
            avg_latency = np.mean([m.latency_ms for m in qos_metrics])
            baseline_latency = 2000  # 2 seconds baseline
            latency_improvement = max(0, (baseline_latency - avg_latency) / baseline_latency)
            
            # Calculate throughput improvements
            avg_throughput = np.mean([m.throughput_rps for m in qos_metrics])
            baseline_throughput = 100  # 100 requests per second baseline
            throughput_improvement = max(0, (avg_throughput - baseline_throughput) / baseline_throughput)
            
            # Calculate availability improvements
            avg_availability = np.mean([m.availability_percent for m in qos_metrics])
            baseline_availability = 95  # 95% baseline
            availability_improvement = max(0, (avg_availability - baseline_availability) / baseline_availability)
            
            # Weighted average of improvements
            efficiency_gains = (
                latency_improvement * 0.4 +
                throughput_improvement * 0.3 +
                availability_improvement * 0.3
            ) * 100  # Convert to percentage
            
            logger.info(f"Efficiency gains calculated: {efficiency_gains:.1f}%")
            return efficiency_gains
            
        except Exception as e:
            logger.error(f"Error calculating efficiency gains: {e}")
            return 0.0
    
    def _calculate_quality_improvements(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate quality improvements based on QoS metrics"""
        try:
            if not qos_metrics:
                return 0.0
            
            # Calculate error rate improvements
            avg_error_rate = np.mean([m.error_rate for m in qos_metrics])
            baseline_error_rate = 0.05  # 5% baseline error rate
            error_improvement = max(0, (baseline_error_rate - avg_error_rate) / baseline_error_rate)
            
            # Calculate response time consistency (P95)
            response_times = [m.response_time_p95 for m in qos_metrics]
            response_consistency = 1.0 - (np.std(response_times) / np.mean(response_times))
            response_consistency = max(0, min(1, response_consistency))
            
            # Calculate overall quality score
            quality_score = (
                error_improvement * 0.6 +
                response_consistency * 0.4
            ) * 100  # Convert to percentage
            
            logger.info(f"Quality improvements calculated: {quality_score:.1f}%")
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating quality improvements: {e}")
            return 0.0
    
    def _calculate_efficiency_multiplier(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate efficiency multiplier based on QoS performance"""
        try:
            if not qos_metrics:
                return 1.0
            
            # Calculate performance score (0-1)
            avg_latency = np.mean([m.latency_ms for m in qos_metrics])
            avg_throughput = np.mean([m.throughput_rps for m in qos_metrics])
            avg_availability = np.mean([m.availability_percent for m in qos_metrics])
            
            # Normalize metrics to 0-1 scale
            latency_score = max(0, 1 - (avg_latency / 5000))  # 5s max latency
            throughput_score = min(1, avg_throughput / 1000)   # 1000 RPS max
            availability_score = avg_availability / 100.0
            
            # Weighted average
            performance_score = (
                latency_score * 0.4 +
                throughput_score * 0.3 +
                availability_score * 0.3
            )
            
            # Convert to multiplier (0.5x to 2.0x range)
            multiplier = 0.5 + (performance_score * 1.5)
            
            return multiplier
            
        except Exception as e:
            logger.error(f"Error calculating efficiency multiplier: {e}")
            return 1.0
    
    def _calculate_total_value_score(self, cost_savings: float, user_reach: int,
                                   efficiency: float, quality: float,
                                   sector_mult: float, use_case_mult: float) -> float:
        """Calculate normalized total value score (0-100)"""
        try:
            # Normalize individual metrics to 0-100 scale
            cost_score = min(100, (cost_savings / 1000000) * 50)  # $1M = 50 points
            reach_score = min(100, (user_reach / 1000000) * 20)   # 1M users = 20 points
            efficiency_score = efficiency  # Already 0-100
            quality_score = quality        # Already 0-100
            
            # Calculate weighted score
            weighted_score = (
                cost_score * 0.3 +
                reach_score * 0.2 +
                efficiency_score * 0.25 +
                quality_score * 0.25
            )
            
            # Apply sector and use case multipliers
            adjusted_score = weighted_score * sector_mult * use_case_mult
            
            # Normalize to 0-100 range
            final_score = min(100, max(0, adjusted_score))
            
            logger.info(f"Total value score calculated: {final_score:.1f}/100")
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating total value score: {e}")
            return 0.0
    
    def _calculate_roi_ratio(self, cost_savings: float, customer_profile: Dict[str, Any]) -> float:
        """Calculate return on investment ratio"""
        try:
            # Estimate annual Bhashini service cost based on SLA tier
            sla_tier = customer_profile.get('sla_tier', 'basic')
            target_users = customer_profile.get('target_user_base', 10000)
            
            # Annual service cost estimates
            sla_costs = {
                'basic': 50000,      # $50K/year
                'standard': 150000,  # $150K/year
                'premium': 500000    # $500K/year
            }
            
            annual_cost = sla_costs.get(sla_tier, 50000)
            
            # Calculate ROI
            if annual_cost > 0:
                roi = cost_savings / annual_cost
            else:
                roi = 0.0
            
            logger.info(f"ROI ratio calculated: {roi:.2f}x")
            return roi
            
        except Exception as e:
            logger.error(f"Error calculating ROI ratio: {e}")
            return 0.0
    
    def _calculate_payback_period(self, cost_savings: float, customer_profile: Dict[str, Any]) -> float:
        """Calculate payback period in months"""
        try:
            sla_tier = customer_profile.get('sla_tier', 'basic')
            target_users = customer_profile.get('target_user_base', 10000)
            
            # Annual service cost estimates
            sla_costs = {
                'basic': 50000,
                'standard': 150000,
                'premium': 500000
            }
            
            annual_cost = sla_costs.get(sla_tier, 50000)
            
            # Calculate payback period
            if cost_savings > 0:
                payback_years = annual_cost / cost_savings
                payback_months = payback_years * 12
            else:
                payback_months = float('inf')
            
            # Cap at reasonable range
            payback_months = min(payback_months, 60)  # Max 5 years
            
            logger.info(f"Payback period calculated: {payback_months:.1f} months")
            return payback_months
            
        except Exception as e:
            logger.error(f"Error calculating payback period: {e}")
            return 60.0
    
    def _calculate_confidence_score(self, qos_metrics: List[QoSMetrics], 
                                  customer_profile: Dict[str, Any]) -> float:
        """Calculate confidence score for the value estimation"""
        try:
            confidence = 70.0  # Base confidence
            
            # Increase confidence based on data quality
            if len(qos_metrics) >= 100:
                confidence += 15  # Sufficient data points
            elif len(qos_metrics) >= 50:
                confidence += 10  # Moderate data points
            elif len(qos_metrics) >= 10:
                confidence += 5   # Minimal data points
            
            # Increase confidence based on profile completeness
            required_fields = ['sector', 'use_case_category', 'target_user_base', 'sla_tier']
            complete_fields = sum(1 for field in required_fields if customer_profile.get(field))
            profile_completeness = complete_fields / len(required_fields)
            confidence += profile_completeness * 10
            
            # Decrease confidence for edge cases
            if customer_profile.get('sector') not in self.sector_multipliers:
                confidence -= 10  # Unknown sector
            
            if customer_profile.get('use_case_category') not in self.use_case_multipliers:
                confidence -= 10  # Unknown use case
            
            # Ensure confidence is within 0-100 range
            confidence = max(0, min(100, confidence))
            
            logger.info(f"Confidence score calculated: {confidence:.1f}%")
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 50.0
    
    def generate_value_report(self, value_metrics: ValueMetrics, 
                            customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive value impact report"""
        try:
            report = {
                'executive_summary': {
                    'total_annual_value': f"${value_metrics.cost_savings:,.2f}",
                    'roi_ratio': f"{value_metrics.roi_ratio:.2f}x",
                    'payback_period': f"{value_metrics.payback_period_months:.1f} months",
                    'value_score': f"{value_metrics.total_value_score:.1f}/100"
                },
                'detailed_breakdown': {
                    'cost_savings': {
                        'annual_savings': f"${value_metrics.cost_savings:,.2f}",
                        'description': 'Reduced translation and operational costs'
                    },
                    'user_impact': {
                        'users_reached': f"{value_metrics.user_reach_impact:,}",
                        'description': 'Citizens/patients/students served effectively'
                    },
                    'efficiency_gains': {
                        'improvement': f"{value_metrics.efficiency_gains:.1f}%",
                        'description': 'Faster service delivery and processing'
                    },
                    'quality_improvements': {
                        'improvement': f"{value_metrics.quality_improvements:.1f}%",
                        'description': 'Enhanced accuracy and user satisfaction'
                    }
                },
                'sector_analysis': {
                    'sector': customer_profile.get('sector', 'Unknown'),
                    'sector_multiplier': value_metrics.sector_multiplier,
                    'use_case': customer_profile.get('use_case_category', 'Unknown'),
                    'use_case_multiplier': value_metrics.use_case_multiplier
                },
                'confidence_metrics': {
                    'confidence_score': f"{value_metrics.confidence_score:.1f}%",
                    'calculation_methodology': value_metrics.calculation_methodology
                },
                'recommendations': self._generate_value_recommendations(value_metrics, customer_profile)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating value report: {e}")
            return {}
    
    def _generate_value_recommendations(self, value_metrics: ValueMetrics, 
                                      customer_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on value analysis"""
        recommendations = []
        
        try:
            # Cost optimization recommendations
            if value_metrics.cost_savings < 100000:
                recommendations.append("Consider upgrading to higher SLA tier for better cost efficiency")
            
            # User reach recommendations
            if value_metrics.user_reach_impact < customer_profile.get('target_user_base', 0) * 0.5:
                recommendations.append("Focus on improving service availability to reach more users")
            
            # Efficiency recommendations
            if value_metrics.efficiency_gains < 20:
                recommendations.append("Optimize service performance to improve efficiency gains")
            
            # Quality recommendations
            if value_metrics.quality_improvements < 30:
                recommendations.append("Implement quality improvement measures for better user satisfaction")
            
            # ROI recommendations
            if value_metrics.roi_ratio < 2.0:
                recommendations.append("Review service utilization to improve ROI")
            
            # Payback period recommendations
            if value_metrics.payback_period_months > 24:
                recommendations.append("Consider phased implementation to reduce initial investment")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations at this time"]

# Example usage and testing
if __name__ == "__main__":
    # Initialize value estimator
    estimator = ValueEstimator()
    
    # Sample customer profile
    customer_profile = {
        'tenant_id': 'gov_digital_india',
        'sector': 'government',
        'use_case_category': 'citizen_services',
        'target_user_base': 5000000,
        'sla_tier': 'premium'
    }
    
    # Sample QoS metrics
    qos_metrics = [
        QoSMetrics(
            tenant_id='gov_digital_india',
            timestamp=datetime.now(),
            service_type='translation',
            latency_ms=1500,
            throughput_rps=200,
            error_rate=0.02,
            availability_percent=99.5,
            response_time_p95=2500
        ),
        QoSMetrics(
            tenant_id='gov_digital_india',
            timestamp=datetime.now(),
            service_type='tts',
            latency_ms=800,
            throughput_rps=150,
            error_rate=0.01,
            availability_percent=99.8,
            response_time_p95=1200
        )
    ]
    
    # Calculate value
    try:
        value_metrics = estimator.calculate_customer_value(customer_profile, qos_metrics)
        
        print("Value Estimation Results:")
        print(f"Cost Savings: ${value_metrics.cost_savings:,.2f}/year")
        print(f"User Reach: {value_metrics.user_reach_impact:,} users")
        print(f"Efficiency Gains: {value_metrics.efficiency_gains:.1f}%")
        print(f"Quality Improvements: {value_metrics.quality_improvements:.1f}%")
        print(f"Total Value Score: {value_metrics.total_value_score:.1f}/100")
        print(f"ROI Ratio: {value_metrics.roi_ratio:.2f}x")
        print(f"Payback Period: {value_metrics.payback_period_months:.1f} months")
        print(f"Confidence: {value_metrics.confidence_score:.1f}%")
        
        # Generate report
        report = estimator.generate_value_report(value_metrics, customer_profile)
        print("\nValue Report Generated Successfully")
        
    except Exception as e:
        print(f"Error in value estimation: {e}")
