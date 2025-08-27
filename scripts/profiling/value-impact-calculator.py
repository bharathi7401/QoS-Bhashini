#!/usr/bin/env python3
"""
Value Impact Calculator for Bhashini Business Intelligence System

This module provides comprehensive value and impact calculation capabilities
for processing customer profiles and QoS metrics to generate business value estimates.

Features:
- Cost savings calculations (translation costs, operational efficiency)
- User reach impact analysis (number of people served, accessibility)
- Time savings quantification (faster service delivery, automation)
- Quality improvements measurement (accuracy gains, user satisfaction)
- Sector-specific calculation models
- Historical trend analysis
- ROI calculations and benchmarking
- Value projection and reporting

Author: Bhashini BI Team
Date: 2024
"""

import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import math
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class QoSMetrics:
    """QoS metrics for value calculation"""
    availability_percent: float
    response_time_p95: float
    error_rate: float
    throughput_rps: float
    latency_p95: float
    timestamp: datetime
    service_type: str  # Translation, TTS, ASR


@dataclass
class ValueMetrics:
    """Calculated value metrics"""
    cost_savings: float
    user_reach_impact: int
    efficiency_gains: float
    quality_improvements: float
    total_value_score: float
    confidence_score: float
    roi_ratio: float
    payback_period_months: float
    calculation_timestamp: datetime
    calculation_methodology: str


@dataclass
class CustomerProfile:
    """Customer profile for value calculation"""
    tenant_id: str
    organization_name: str
    sector: str
    use_case_category: str
    target_user_base: int
    geographical_coverage: List[str]
    languages_required: List[str]
    sla_tier: str
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None


@dataclass
class ValueCalculationResult:
    """Result of value calculation"""
    customer_profile: CustomerProfile
    value_metrics: ValueMetrics
    qos_metrics_summary: Dict[str, Any]
    sector_analysis: Dict[str, Any]
    recommendations: List[str]
    calculation_errors: List[str] = None


class ValueImpactCalculator:
    """
    Comprehensive value and impact calculation system
    """
    
    def __init__(self, config_path: str = "config/sector-kpis.yml"):
        """
        Initialize the value impact calculator
        
        Args:
            config_path: Path to sector KPI configuration file
        """
        self.config_path = Path(config_path)
        self.sector_config = self._load_sector_config()
        self.calculation_models = self._load_calculation_models()
        self.benchmark_data = self._load_benchmark_data()
        
        # Calculation statistics
        self.calculation_stats = {
            "total_calculations": 0,
            "successful_calculations": 0,
            "failed_calculations": 0,
            "average_processing_time": 0.0
        }
    
    def _load_sector_config(self) -> Dict[str, Any]:
        """Load sector-specific configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Sector config file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading sector config: {e}")
            return {}
    
    def _load_calculation_models(self) -> Dict[str, Any]:
        """Load calculation models and formulas"""
        return {
            "cost_savings": {
                "translation_cost_per_word": 0.15,  # USD per word
                "manual_processing_cost_per_hour": 25.0,  # USD per hour
                "automation_efficiency_gain": 0.7,  # 70% efficiency improvement
                "sector_multipliers": {
                    "government": 1.2,
                    "healthcare": 1.5,
                    "education": 1.1,
                    "private": 1.0,
                    "NGO": 0.8
                }
            },
            "user_reach": {
                "accessibility_improvement": 0.3,  # 30% improvement in accessibility
                "language_coverage_multiplier": 0.25,  # 25% improvement per additional language
                "sector_impact_multipliers": {
                    "government": 1.5,  # High public impact
                    "healthcare": 1.8,  # Critical for patient care
                    "education": 1.3,   # Important for learning
                    "private": 1.0,     # Standard business impact
                    "NGO": 1.4         # Community impact
                }
            },
            "efficiency": {
                "response_time_improvement": 0.4,  # 40% improvement in response time
                "availability_improvement": 0.2,   # 20% improvement in availability
                "error_reduction_impact": 0.6,    # 60% impact from error reduction
                "sector_efficiency_multipliers": {
                    "government": 1.3,
                    "healthcare": 1.6,
                    "education": 1.2,
                    "private": 1.0,
                    "NGO": 1.1
                }
            },
            "quality": {
                "accuracy_improvement": 0.5,      # 50% improvement in accuracy
                "user_satisfaction_gain": 0.4,    # 40% improvement in satisfaction
                "compliance_improvement": 0.3,    # 30% improvement in compliance
                "sector_quality_multipliers": {
                    "government": 1.4,
                    "healthcare": 1.7,
                    "education": 1.3,
                    "private": 1.0,
                    "NGO": 1.2
                }
            }
        }
    
    def _load_benchmark_data(self) -> Dict[str, Any]:
        """Load industry benchmark data for comparison"""
        return {
            "translation_services": {
                "average_cost_per_word": 0.18,
                "average_accuracy": 0.85,
                "average_response_time": 2.5
            },
            "tts_services": {
                "average_cost_per_minute": 0.05,
                "average_quality_score": 3.8,
                "average_response_time": 1.2
            },
            "asr_services": {
                "average_cost_per_minute": 0.03,
                "average_accuracy": 0.88,
                "average_response_time": 0.8
            },
            "sector_benchmarks": {
                "government": {
                    "average_availability": 99.2,
                    "average_response_time": 3.0,
                    "compliance_score": 92.0
                },
                "healthcare": {
                    "average_availability": 99.8,
                    "average_response_time": 1.5,
                    "accuracy_score": 96.0
                },
                "education": {
                    "average_availability": 98.5,
                    "average_response_time": 2.8,
                    "content_quality": 87.0
                },
                "private": {
                    "average_availability": 99.0,
                    "average_response_time": 2.2,
                    "user_satisfaction": 4.1
                },
                "NGO": {
                    "average_availability": 97.5,
                    "average_response_time": 3.5,
                    "community_impact": 78.0
                }
            }
        }
    
    def calculate_customer_value(self, customer_profile: CustomerProfile, 
                               qos_metrics: List[QoSMetrics]) -> ValueCalculationResult:
        """
        Calculate comprehensive value metrics for a customer
        
        Args:
            customer_profile: Customer profile information
            qos_metrics: List of QoS metrics for analysis
            
        Returns:
            ValueCalculationResult with calculated metrics and analysis
        """
        start_time = datetime.now()
        
        try:
            # Validate inputs
            if not qos_metrics:
                raise ValueError("QoS metrics list cannot be empty")
            
            # Calculate individual value components
            cost_savings = self._calculate_cost_savings(customer_profile, qos_metrics)
            user_reach_impact = self._calculate_user_reach_impact(customer_profile, qos_metrics)
            efficiency_gains = self._calculate_efficiency_gains(customer_profile, qos_metrics)
            quality_improvements = self._calculate_quality_improvements(customer_profile, qos_metrics)
            
            # Calculate total value score
            total_value_score = self._calculate_total_value_score(
                cost_savings, user_reach_impact, efficiency_gains, quality_improvements
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(qos_metrics, customer_profile)
            
            # Calculate ROI and payback period
            roi_ratio = self._calculate_roi_ratio(cost_savings, customer_profile)
            payback_period_months = self._calculate_payback_period(cost_savings, customer_profile)
            
            # Create value metrics
            value_metrics = ValueMetrics(
                cost_savings=cost_savings,
                user_reach_impact=user_reach_impact,
                efficiency_gains=efficiency_gains,
                quality_improvements=quality_improvements,
                total_value_score=total_value_score,
                confidence_score=confidence_score,
                roi_ratio=roi_ratio,
                payback_period_months=payback_period_months,
                calculation_timestamp=datetime.now(),
                calculation_methodology="comprehensive_value_analysis"
            )
            
            # Generate analysis and recommendations
            qos_summary = self._generate_qos_summary(qos_metrics)
            sector_analysis = self._analyze_sector_context(customer_profile, qos_metrics)
            recommendations = self._generate_recommendations(customer_profile, value_metrics, qos_metrics)
            
            # Update statistics
            self._update_calculation_stats(True, start_time)
            
            return ValueCalculationResult(
                customer_profile=customer_profile,
                value_metrics=value_metrics,
                qos_metrics_summary=qos_summary,
                sector_analysis=sector_analysis,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error calculating customer value: {e}")
            self._update_calculation_stats(False, start_time)
            
            return ValueCalculationResult(
                customer_profile=customer_profile,
                value_metrics=None,
                qos_metrics_summary={},
                sector_analysis={},
                recommendations=[],
                calculation_errors=[str(e)]
            )
    
    def _calculate_cost_savings(self, customer_profile: CustomerProfile, 
                              qos_metrics: List[QoSMetrics]) -> float:
        """Calculate cost savings from Bhashini services"""
        base_cost_savings = 0.0
        
        # Calculate translation cost savings
        translation_metrics = [m for m in qos_metrics if m.service_type == "Translation"]
        if translation_metrics:
            avg_accuracy = statistics.mean([1 - m.error_rate for m in translation_metrics])
            words_processed = customer_profile.target_user_base * 100  # Estimate: 100 words per user
            manual_cost = words_processed * self.calculation_models["cost_savings"]["translation_cost_per_word"]
            automated_cost = manual_cost * (1 - avg_accuracy) * 0.3  # 30% of manual cost
            base_cost_savings += manual_cost - automated_cost
        
        # Calculate operational efficiency savings
        efficiency_gain = self.calculation_models["cost_savings"]["automation_efficiency_gain"]
        if customer_profile.employee_count:
            hourly_savings = customer_profile.employee_count * efficiency_gain * 2  # 2 hours per employee
            operational_savings = hourly_savings * self.calculation_models["cost_savings"]["manual_processing_cost_per_hour"]
            base_cost_savings += operational_savings
        
        # Apply sector multiplier
        sector_multiplier = self.calculation_models["cost_savings"]["sector_multipliers"].get(
            customer_profile.sector, 1.0
        )
        
        return base_cost_savings * sector_multiplier
    
    def _calculate_user_reach_impact(self, customer_profile: CustomerProfile, 
                                   qos_metrics: List[QoSMetrics]) -> int:
        """Calculate user reach impact from improved accessibility and language coverage"""
        base_impact = 0
        
        # Accessibility improvement impact
        availability_metrics = [m.availability_percent for m in qos_metrics]
        if availability_metrics:
            avg_availability = statistics.mean(availability_metrics)
            availability_improvement = max(0, avg_availability - 95.0) / 100.0  # Base 95%
            accessibility_impact = int(customer_profile.target_user_base * 
                                    self.calculation_models["user_reach"]["accessibility_improvement"] *
                                    availability_improvement)
            base_impact += accessibility_impact
        
        # Language coverage impact
        language_multiplier = len(customer_profile.languages_required) * \
                            self.calculation_models["user_reach"]["language_coverage_multiplier"]
        language_impact = int(customer_profile.target_user_base * language_multiplier)
        base_impact += language_impact
        
        # Apply sector impact multiplier
        sector_multiplier = self.calculation_models["user_reach"]["sector_impact_multipliers"].get(
            customer_profile.sector, 1.0
        )
        
        return int(base_impact * sector_multiplier)
    
    def _calculate_efficiency_gains(self, customer_profile: CustomerProfile, 
                                  qos_metrics: List[QosMetrics]) -> float:
        """Calculate efficiency gains from improved performance"""
        efficiency_score = 0.0
        
        # Response time improvements
        response_times = [m.response_time_p95 for m in qos_metrics]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            benchmark_response = self.benchmark_data["sector_benchmarks"][customer_profile.sector]["average_response_time"]
            response_improvement = max(0, benchmark_response - avg_response_time) / benchmark_response
            efficiency_score += response_improvement * self.calculation_models["efficiency"]["response_time_improvement"]
        
        # Availability improvements
        availability_scores = [m.availability_percent for m in qos_metrics]
        if availability_scores:
            avg_availability = statistics.mean(availability_scores)
            benchmark_availability = self.benchmark_data["sector_benchmarks"][customer_profile.sector]["average_availability"]
            availability_improvement = max(0, avg_availability - benchmark_availability) / 100.0
            efficiency_score += availability_improvement * self.calculation_models["efficiency"]["availability_improvement"]
        
        # Error reduction impact
        error_rates = [m.error_rate for m in qos_metrics]
        if error_rates:
            avg_error_rate = statistics.mean(error_rates)
            error_reduction = max(0, 0.05 - avg_error_rate) / 0.05  # Base 5% error rate
            efficiency_score += error_reduction * self.calculation_models["efficiency"]["error_reduction_impact"]
        
        # Apply sector efficiency multiplier
        sector_multiplier = self.calculation_models["efficiency"]["sector_efficiency_multipliers"].get(
            customer_profile.sector, 1.0
        )
        
        return efficiency_score * sector_multiplier
    
    def _calculate_quality_improvements(self, customer_profile: CustomerProfile, 
                                     qos_metrics: List[QoSMetrics]) -> float:
        """Calculate quality improvements from better accuracy and user satisfaction"""
        quality_score = 0.0
        
        # Accuracy improvements
        error_rates = [m.error_rate for m in qos_metrics]
        if error_rates:
            avg_error_rate = statistics.mean(error_rates)
            accuracy_improvement = max(0, 0.05 - avg_error_rate) / 0.05  # Base 5% error rate
            quality_score += accuracy_improvement * self.calculation_models["quality"]["accuracy_improvement"]
        
        # Availability improvements (proxy for reliability)
        availability_scores = [m.availability_percent for m in qos_metrics]
        if availability_scores:
            avg_availability = statistics.mean(availability_scores)
            reliability_improvement = max(0, avg_availability - 95.0) / 100.0  # Base 95%
            quality_score += reliability_improvement * self.calculation_models["quality"]["compliance_improvement"]
        
        # Throughput improvements (proxy for service quality)
        throughput_scores = [m.throughput_rps for m in qos_metrics]
        if throughput_scores:
            avg_throughput = statistics.mean(throughput_scores)
            throughput_improvement = min(1.0, avg_throughput / 100.0)  # Normalize to 100 RPS
            quality_score += throughput_improvement * self.calculation_models["quality"]["user_satisfaction_gain"]
        
        # Apply sector quality multiplier
        sector_multiplier = self.calculation_models["quality"]["sector_quality_multipliers"].get(
            customer_profile.sector, 1.0
        )
        
        return quality_score * sector_multiplier
    
    def _calculate_total_value_score(self, cost_savings: float, user_reach_impact: int,
                                   efficiency_gains: float, quality_improvements: float) -> float:
        """Calculate total value score from all components"""
        # Normalize components to 0-100 scale
        normalized_cost = min(100, cost_savings / 10000)  # Normalize to $10K max
        normalized_reach = min(100, user_reach_impact / 10000)  # Normalize to 10K users max
        normalized_efficiency = efficiency_gains * 100  # Already 0-1 scale
        normalized_quality = quality_improvements * 100  # Already 0-1 scale
        
        # Weighted combination
        weights = {
            "cost": 0.35,      # 35% weight for cost savings
            "reach": 0.25,     # 25% weight for user reach
            "efficiency": 0.25, # 25% weight for efficiency
            "quality": 0.15    # 15% weight for quality
        }
        
        total_score = (
            normalized_cost * weights["cost"] +
            normalized_reach * weights["reach"] +
            normalized_efficiency * weights["efficiency"] +
            normalized_quality * weights["quality"]
        )
        
        return round(total_score, 2)
    
    def _calculate_confidence_score(self, qos_metrics: List[QoSMetrics], 
                                  customer_profile: CustomerProfile) -> float:
        """Calculate confidence score for the value calculation"""
        confidence_factors = []
        
        # Data completeness factor
        required_metrics = ["availability_percent", "response_time_p95", "error_rate"]
        completeness_score = 0.0
        
        for metric_name in required_metrics:
            metric_values = [getattr(m, metric_name) for m in qos_metrics if hasattr(m, metric_name)]
            if metric_values:
                completeness_score += 1.0
        
        completeness_score /= len(required_metrics)
        confidence_factors.append(completeness_score)
        
        # Data consistency factor
        if len(qos_metrics) > 1:
            availability_values = [m.availability_percent for m in qos_metrics]
            consistency_score = 1.0 - (statistics.stdev(availability_values) / 100.0)
            consistency_score = max(0.0, min(1.0, consistency_score))
            confidence_factors.append(consistency_score)
        else:
            confidence_factors.append(0.5)  # Single data point
        
        # Profile completeness factor
        profile_fields = [customer_profile.sector, customer_profile.use_case_category, 
                         customer_profile.target_user_base, customer_profile.sla_tier]
        profile_completeness = sum(1 for field in profile_fields if field) / len(profile_fields)
        confidence_factors.append(profile_completeness)
        
        # Calculate average confidence
        avg_confidence = statistics.mean(confidence_factors)
        return round(avg_confidence, 3)
    
    def _calculate_roi_ratio(self, cost_savings: float, customer_profile: CustomerProfile) -> float:
        """Calculate ROI ratio based on cost savings and estimated service costs"""
        # Estimate annual service cost (rough calculation)
        base_service_cost = 5000  # Base annual cost
        
        # Adjust for user base size
        if customer_profile.target_user_base > 100000:
            service_cost_multiplier = 3.0
        elif customer_profile.target_user_base > 10000:
            service_cost_multiplier = 2.0
        else:
            service_cost_multiplier = 1.0
        
        # Adjust for SLA tier
        sla_multipliers = {"basic": 1.0, "standard": 1.5, "premium": 2.5}
        sla_multiplier = sla_multipliers.get(customer_profile.sla_tier, 1.0)
        
        estimated_service_cost = base_service_cost * service_cost_multiplier * sla_multiplier
        
        # Calculate ROI
        if estimated_service_cost > 0:
            roi_ratio = cost_savings / estimated_service_cost
        else:
            roi_ratio = 0.0
        
        return round(roi_ratio, 2)
    
    def _calculate_payback_period(self, cost_savings: float, customer_profile: CustomerProfile) -> float:
        """Calculate payback period in months"""
        # Estimate annual service cost (same logic as ROI)
        base_service_cost = 5000
        if customer_profile.target_user_base > 100000:
            service_cost_multiplier = 3.0
        elif customer_profile.target_user_base > 10000:
            service_cost_multiplier = 2.0
        else:
            service_cost_multiplier = 1.0
        
        sla_multipliers = {"basic": 1.0, "standard": 1.5, "premium": 2.5}
        sla_multiplier = sla_multipliers.get(customer_profile.sla_tier, 1.0)
        
        estimated_service_cost = base_service_cost * service_cost_multiplier * sla_multiplier
        
        # Calculate payback period
        if cost_savings > 0:
            payback_months = (estimated_service_cost / cost_savings) * 12
        else:
            payback_months = float('inf')
        
        return round(payback_months, 1)
    
    def _generate_qos_summary(self, qos_metrics: List[QoSMetrics]) -> Dict[str, Any]:
        """Generate summary of QoS metrics"""
        if not qos_metrics:
            return {}
        
        summary = {
            "total_metrics": len(qos_metrics),
            "service_types": list(set(m.service_type for m in qos_metrics)),
            "time_range": {
                "start": min(m.timestamp for m in qos_metrics).isoformat(),
                "end": max(m.timestamp for m in qos_metrics).isoformat()
            },
            "averages": {},
            "trends": {}
        }
        
        # Calculate averages for each metric type
        metric_fields = ["availability_percent", "response_time_p95", "error_rate", "throughput_rps", "latency_p95"]
        
        for field in metric_fields:
            values = [getattr(m, field) for m in qos_metrics if hasattr(m, field)]
            if values:
                summary["averages"][field] = round(statistics.mean(values), 3)
        
        # Calculate trends (simple linear trend)
        if len(qos_metrics) > 1:
            sorted_metrics = sorted(qos_metrics, key=lambda x: x.timestamp)
            for field in metric_fields:
                values = [getattr(m, field) for m in sorted_metrics if hasattr(m, field)]
                if len(values) > 1:
                    # Simple trend calculation
                    trend = (values[-1] - values[0]) / len(values)
                    summary["trends"][field] = round(trend, 4)
        
        return summary
    
    def _analyze_sector_context(self, customer_profile: CustomerProfile, 
                              qos_metrics: List[QoSMetrics]) -> Dict[str, Any]:
        """Analyze sector-specific context and performance"""
        sector = customer_profile.sector
        sector_benchmarks = self.benchmark_data["sector_benchmarks"].get(sector, {})
        
        analysis = {
            "sector": sector,
            "benchmark_comparison": {},
            "sector_specific_insights": [],
            "performance_rating": "Unknown"
        }
        
        if not qos_metrics:
            return analysis
        
        # Compare with sector benchmarks
        avg_availability = statistics.mean([m.availability_percent for m in qos_metrics])
        avg_response_time = statistics.mean([m.response_time_p95 for m in qos_metrics])
        
        if "average_availability" in sector_benchmarks:
            availability_diff = avg_availability - sector_benchmarks["average_availability"]
            analysis["benchmark_comparison"]["availability"] = {
                "current": round(avg_availability, 2),
                "benchmark": sector_benchmarks["average_availability"],
                "difference": round(availability_diff, 2),
                "status": "Above" if availability_diff > 0 else "Below"
            }
        
        if "average_response_time" in sector_benchmarks:
            response_diff = sector_benchmarks["average_response_time"] - avg_response_time
            analysis["benchmark_comparison"]["response_time"] = {
                "current": round(avg_response_time, 2),
                "benchmark": sector_benchmarks["average_response_time"],
                "difference": round(response_diff, 2),
                "status": "Above" if response_diff > 0 else "Below"
            }
        
        # Generate sector-specific insights
        if sector == "healthcare":
            if avg_availability < 99.5:
                analysis["sector_specific_insights"].append(
                    "Healthcare requires 99.5%+ availability for patient safety"
                )
            if avg_response_time > 2.0:
                analysis["sector_specific_insights"].append(
                    "Response time should be under 2 seconds for critical communications"
                )
        
        elif sector == "government":
            if avg_availability < 99.0:
                analysis["sector_specific_insights"].append(
                    "Government services require high availability for citizen access"
                )
        
        # Calculate performance rating
        performance_score = 0
        if avg_availability >= 99.5:
            performance_score += 40
        elif avg_availability >= 99.0:
            performance_score += 30
        elif avg_availability >= 98.0:
            performance_score += 20
        
        if avg_response_time <= 1.0:
            performance_score += 30
        elif avg_response_time <= 2.0:
            performance_score += 20
        elif avg_response_time <= 3.0:
            performance_score += 10
        
        if performance_score >= 60:
            analysis["performance_rating"] = "Excellent"
        elif performance_score >= 40:
            analysis["performance_rating"] = "Good"
        elif performance_score >= 20:
            analysis["performance_rating"] = "Fair"
        else:
            analysis["performance_rating"] = "Poor"
        
        return analysis
    
    def _generate_recommendations(self, customer_profile: CustomerProfile, 
                                value_metrics: ValueMetrics, 
                                qos_metrics: List[QoSMetrics]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if not qos_metrics:
            return ["Insufficient QoS data for recommendations"]
        
        # Performance-based recommendations
        avg_availability = statistics.mean([m.availability_percent for m in qos_metrics])
        avg_response_time = statistics.mean([m.response_time_p95 for m in qos_metrics])
        avg_error_rate = statistics.mean([m.error_rate for m in qos_metrics])
        
        if avg_availability < 99.0:
            recommendations.append(
                "Consider upgrading infrastructure to improve availability above 99%"
            )
        
        if avg_response_time > 3.0:
            recommendations.append(
                "Optimize service performance to reduce response time below 3 seconds"
            )
        
        if avg_error_rate > 0.05:
            recommendations.append(
                "Implement error handling improvements to reduce error rate below 5%"
            )
        
        # Value-based recommendations
        if value_metrics.roi_ratio < 2.0:
            recommendations.append(
                "Focus on cost optimization to improve ROI above 2:1"
            )
        
        if value_metrics.payback_period_months > 12:
            recommendations.append(
                "Implement efficiency improvements to achieve payback within 12 months"
            )
        
        # Sector-specific recommendations
        if customer_profile.sector == "healthcare":
            recommendations.append(
                "Prioritize availability and accuracy for patient safety compliance"
            )
        elif customer_profile.sector == "government":
            recommendations.append(
                "Ensure high availability during business hours for citizen services"
            )
        elif customer_profile.sector == "education":
            recommendations.append(
                "Focus on content quality and accessibility for learning outcomes"
            )
        
        # Language and coverage recommendations
        if len(customer_profile.languages_required) < 3:
            recommendations.append(
                "Consider expanding language coverage to reach more diverse user base"
            )
        
        if len(customer_profile.geographical_coverage) < 2:
            recommendations.append(
                "Evaluate expanding geographical coverage for broader service reach"
            )
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _update_calculation_stats(self, success: bool, start_time: datetime):
        """Update calculation statistics"""
        self.calculation_stats["total_calculations"] += 1
        
        if success:
            self.calculation_stats["successful_calculations"] += 1
        else:
            self.calculation_stats["failed_calculations"] += 1
        
        # Update average processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        current_avg = self.calculation_stats["average_processing_time"]
        total_successful = self.calculation_stats["successful_calculations"]
        
        if total_successful > 0:
            new_avg = ((current_avg * (total_successful - 1)) + processing_time) / total_successful
            self.calculation_stats["average_processing_time"] = round(new_avg, 3)
    
    def get_calculation_stats(self) -> Dict[str, Any]:
        """Get calculation statistics"""
        total = self.calculation_stats["total_calculations"]
        if total == 0:
            success_rate = 0.0
        else:
            success_rate = (self.calculation_stats["successful_calculations"] / total) * 100
        
        return {
            **self.calculation_stats,
            "success_rate_percentage": round(success_rate, 2),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_value_report(self, result: ValueCalculationResult, 
                          output_path: str) -> bool:
        """
        Export value calculation report to JSON file
        
        Args:
            result: Value calculation result
            output_path: Path to output JSON file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            report_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "calculator_version": "1.0.0",
                    "calculation_methodology": "comprehensive_value_analysis"
                },
                "customer_profile": asdict(result.customer_profile),
                "value_metrics": asdict(result.value_metrics) if result.value_metrics else None,
                "qos_analysis": result.qos_metrics_summary,
                "sector_analysis": result.sector_analysis,
                "recommendations": result.recommendations,
                "calculation_errors": result.calculation_errors or []
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Successfully exported value report to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting value report: {e}")
            return False


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Value Impact Calculator")
    parser.add_argument("--profile", required=True, help="Customer profile JSON file")
    parser.add_argument("--qos-metrics", required=True, help="QoS metrics JSON file")
    parser.add_argument("--output", help="Output report JSON file")
    parser.add_argument("--config", default="config/sector-kpis.yml", help="Sector config path")
    
    args = parser.parse_args()
    
    # Initialize calculator
    calculator = ValueImpactCalculator(args.config)
    
    try:
        # Load customer profile
        with open(args.profile, 'r') as f:
            profile_data = json.load(f)
        
        customer_profile = CustomerProfile(**profile_data)
        
        # Load QoS metrics
        with open(args.qos_metrics, 'r') as f:
            metrics_data = json.load(f)
        
        qos_metrics = [QoSMetrics(**metric) for metric in metrics_data]
        
        # Calculate value
        print("Calculating customer value...")
        result = calculator.calculate_customer_value(customer_profile, qos_metrics)
        
        if result.value_metrics:
            print(f"\nValue Calculation Results:")
            print(f"Cost Savings: ${result.value_metrics.cost_savings:,.2f}")
            print(f"User Reach Impact: {result.value_metrics.user_reach_impact:,} users")
            print(f"Efficiency Gains: {result.value_metrics.efficiency_gains:.2%}")
            print(f"Quality Improvements: {result.value_metrics.quality_improvements:.2%}")
            print(f"Total Value Score: {result.value_metrics.total_value_score}/100")
            print(f"ROI Ratio: {result.value_metrics.roi_ratio}:1")
            print(f"Payback Period: {result.value_metrics.payback_period_months} months")
            print(f"Confidence Score: {result.value_metrics.confidence_score:.1%}")
            
            print(f"\nTop Recommendations:")
            for i, rec in enumerate(result.recommendations[:5], 1):
                print(f"{i}. {rec}")
        else:
            print(f"\nCalculation failed:")
            for error in result.calculation_errors:
                print(f"- {error}")
        
        # Export report if requested
        if args.output:
            calculator.export_value_report(result, args.output)
        
        # Print statistics
        stats = calculator.get_calculation_stats()
        print(f"\nCalculator Statistics:")
        print(f"Total Calculations: {stats['total_calculations']}")
        print(f"Success Rate: {stats['success_rate_percentage']}%")
        print(f"Average Processing Time: {stats['average_processing_time']}s")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
