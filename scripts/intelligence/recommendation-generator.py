#!/usr/bin/env python3
"""
Recommendation Generator for Bhashini Business Intelligence System

This module provides automated recommendation generation capabilities
that analyze customer data and generate personalized optimization suggestions.

Features:
- QoS pattern analysis and anomaly detection
- Customer profile-based recommendation logic
- Sector-specific optimization strategies
- Machine learning pattern recognition
- Recommendation prioritization and scoring
- Integration with annotation system
- Automated delivery and tracking

Author: Bhashini BI Team
Date: 2024
"""

import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import math
import statistics
from dataclasses import dataclass, asdict
import copy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class QoSMetrics:
    """QoS metrics for analysis"""
    availability_percent: float
    response_time_p95: float
    error_rate: float
    throughput_rps: float
    latency_p95: float
    timestamp: datetime
    service_type: str  # Translation, TTS, ASR
    tenant_id: str


@dataclass
class CustomerProfile:
    """Customer profile for recommendations"""
    tenant_id: str
    organization_name: str
    sector: str
    use_case_category: str
    target_user_base: int
    sla_tier: str
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None


@dataclass
class Recommendation:
    """Generated recommendation"""
    recommendation_id: str
    tenant_id: str
    recommendation_type: str
    priority: str
    title: str
    description: str
    expected_impact: str
    implementation_effort: str
    business_value: float
    technical_details: str
    sector_context: str
    use_case_context: str
    confidence_score: float
    status: str = "new"
    created_date: datetime = None
    implemented_date: Optional[datetime] = None


@dataclass
class QoSAnalysis:
    """QoS analysis results"""
    performance_score: float
    reliability_score: float
    capacity_score: float
    utilization_score: float
    anomaly_flags: List[str]
    trend_analysis: Dict[str, Any]
    critical_issues: List[str]
    optimization_opportunities: List[str]


class RecommendationGenerator:
    """
    Automated recommendation generation system
    """
    
    def __init__(self, config_path: str = "config/sector-kpis.yml"):
        """
        Initialize the recommendation generator
        
        Args:
            config_path: Path to sector KPI configuration file
        """
        self.config_path = Path(config_path)
        self.sector_config = self._load_sector_config()
        self.recommendation_templates = self._load_recommendation_templates()
        self.sector_rules = self._load_sector_rules()
        self.use_case_rules = self._load_use_case_rules()
        
        # Recommendation generation metrics
        self.generation_metrics = {
            "total_recommendations_generated": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "sectors_processed": set(),
            "recommendation_types": set()
        }
    
    def _load_sector_config(self) -> Dict[str, Any]:
        """Load sector-specific configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded sector configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load sector configuration: {e}")
            return {}
    
    def _load_recommendation_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load recommendation templates by type"""
        templates = {
            "performance": [
                {
                    "title": "Optimize Response Time",
                    "description": "Implement caching and load balancing to reduce response times",
                    "technical_details": "Add Redis cache layer, implement CDN, optimize database queries",
                    "expected_impact": "high",
                    "implementation_effort": "medium"
                },
                {
                    "title": "Scale Infrastructure",
                    "description": "Add more compute resources to handle peak loads",
                    "technical_details": "Increase ECS task count, add auto-scaling policies",
                    "expected_impact": "high",
                    "implementation_effort": "low"
                }
            ],
            "reliability": [
                {
                    "title": "Improve Error Handling",
                    "description": "Implement circuit breakers and retry mechanisms",
                    "technical_details": "Add resilience4j, implement exponential backoff",
                    "expected_impact": "high",
                    "implementation_effort": "medium"
                },
                {
                    "title": "Enhance Monitoring",
                    "description": "Add comprehensive error tracking and alerting",
                    "technical_details": "Integrate Sentry, add custom metrics, improve alerting",
                    "expected_impact": "medium",
                    "implementation_effort": "low"
                }
            ],
            "capacity": [
                {
                    "title": "Optimize Resource Usage",
                    "description": "Analyze and optimize resource allocation patterns",
                    "technical_details": "Right-size containers, implement resource quotas, monitor usage",
                    "expected_impact": "medium",
                    "implementation_effort": "low"
                },
                {
                    "title": "Implement Auto-scaling",
                    "description": "Add automatic scaling based on demand patterns",
                    "technical_details": "Configure ECS auto-scaling, set up CloudWatch alarms",
                    "expected_impact": "high",
                    "implementation_effort": "medium"
                }
            ],
            "feature_adoption": [
                {
                    "title": "Promote Underutilized Features",
                    "description": "Increase adoption of available Bhashini services",
                    "technical_details": "Create feature guides, implement usage analytics, provide training",
                    "expected_impact": "medium",
                    "implementation_effort": "low"
                }
            ]
        }
        return templates
    
    def _load_sector_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load sector-specific recommendation rules"""
        rules = {
            "government": {
                "priority_factors": ["compliance", "security", "accessibility", "cost_efficiency"],
                "compliance_requirements": ["data_privacy", "accessibility_standards", "regulatory_compliance"],
                "performance_thresholds": {"availability": 99.9, "response_time": 2000, "error_rate": 0.1}
            },
            "healthcare": {
                "priority_factors": ["accuracy", "reliability", "patient_safety", "compliance"],
                "compliance_requirements": ["hipaa", "patient_privacy", "medical_standards"],
                "performance_thresholds": {"availability": 99.99, "response_time": 1000, "error_rate": 0.01}
            },
            "education": {
                "priority_factors": ["accessibility", "content_quality", "user_experience", "cost_efficiency"],
                "compliance_requirements": ["ferpa", "accessibility_standards", "content_standards"],
                "performance_thresholds": {"availability": 99.5, "response_time": 3000, "error_rate": 0.5}
            },
            "private": {
                "priority_factors": ["performance", "cost_efficiency", "user_experience", "scalability"],
                "compliance_requirements": ["data_security", "performance_standards"],
                "performance_thresholds": {"availability": 99.0, "response_time": 5000, "error_rate": 1.0}
            },
            "ngo": {
                "priority_factors": ["accessibility", "community_impact", "cost_efficiency", "transparency"],
                "compliance_requirements": ["transparency", "accessibility_standards"],
                "performance_thresholds": {"availability": 98.0, "response_time": 10000, "error_rate": 2.0}
            }
        }
        return rules
    
    def _load_use_case_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load use case specific recommendation rules"""
        rules = {
            "citizen_services": {
                "critical_metrics": ["availability", "response_time", "accessibility"],
                "optimization_focus": ["performance", "reliability", "accessibility"]
            },
            "healthcare_communication": {
                "critical_metrics": ["accuracy", "response_time", "reliability"],
                "optimization_focus": ["reliability", "accuracy", "performance"]
            },
            "educational_content": {
                "critical_metrics": ["content_quality", "accessibility", "user_experience"],
                "optimization_focus": ["accessibility", "content_quality", "performance"]
            },
            "business_automation": {
                "critical_metrics": ["performance", "scalability", "cost_efficiency"],
                "optimization_focus": ["performance", "capacity", "cost_efficiency"]
            }
        }
        return rules
    
    def analyze_qos_metrics(self, qos_metrics: List[QoSMetrics]) -> QoSAnalysis:
        """Analyze QoS metrics for patterns and issues"""
        if not qos_metrics:
            return QoSAnalysis(
                performance_score=0.0,
                reliability_score=0.0,
                capacity_score=0.0,
                utilization_score=0.0,
                anomaly_flags=[],
                trend_analysis={},
                critical_issues=[],
                optimization_opportunities=[]
            )
        
        # Calculate performance scores
        performance_score = self._calculate_performance_score(qos_metrics)
        reliability_score = self._calculate_reliability_score(qos_metrics)
        capacity_score = self._calculate_capacity_score(qos_metrics)
        utilization_score = self._calculate_utilization_score(qos_metrics)
        
        # Detect anomalies
        anomaly_flags = self._detect_anomalies(qos_metrics)
        
        # Analyze trends
        trend_analysis = self._analyze_trends(qos_metrics)
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(qos_metrics)
        
        # Find optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(qos_metrics)
        
        return QoSAnalysis(
            performance_score=performance_score,
            reliability_score=reliability_score,
            capacity_score=capacity_score,
            utilization_score=utilization_score,
            anomaly_flags=anomaly_flags,
            trend_analysis=trend_analysis,
            critical_issues=critical_issues,
            optimization_opportunities=optimization_opportunities
        )
    
    def _calculate_performance_score(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate overall performance score"""
        if not qos_metrics:
            return 0.0
        
        # Calculate average response time and throughput
        avg_response_time = statistics.mean([m.response_time_p95 for m in qos_metrics])
        avg_throughput = statistics.mean([m.throughput_rps for m in qos_metrics])
        
        # Normalize scores (lower response time = higher score, higher throughput = higher score)
        response_time_score = max(0, 100 - (avg_response_time / 100))  # Normalize to 0-100
        throughput_score = min(100, (avg_throughput / 1000) * 100)  # Normalize to 0-100
        
        # Weighted average
        return (response_time_score * 0.6) + (throughput_score * 0.4)
    
    def _calculate_reliability_score(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate reliability score based on availability and error rates"""
        if not qos_metrics:
            return 0.0
        
        avg_availability = statistics.mean([m.availability_percent for m in qos_metrics])
        avg_error_rate = statistics.mean([m.error_rate for m in qos_metrics])
        
        # Convert error rate to percentage
        avg_error_rate_pct = avg_error_rate * 100
        
        # Calculate scores (higher availability = higher score, lower error rate = higher score)
        availability_score = avg_availability
        error_rate_score = max(0, 100 - avg_error_rate_pct)
        
        # Weighted average
        return (availability_score * 0.7) + (error_rate_score * 0.3)
    
    def _calculate_capacity_score(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate capacity utilization score"""
        if not qos_metrics:
            return 0.0
        
        # Analyze throughput patterns to assess capacity
        throughput_values = [m.throughput_rps for m in qos_metrics]
        max_throughput = max(throughput_values)
        avg_throughput = statistics.mean(throughput_values)
        
        # Capacity score based on throughput stability and utilization
        if max_throughput > 0:
            utilization_ratio = avg_throughput / max_throughput
            # Optimal utilization is around 70-80%
            if utilization_ratio < 0.5:
                return 60.0  # Under-utilized
            elif utilization_ratio < 0.8:
                return 90.0  # Well-utilized
            elif utilization_ratio < 0.95:
                return 70.0  # High utilization
            else:
                return 40.0  # Over-utilized
        else:
            return 0.0
    
    def _calculate_utilization_score(self, qos_metrics: List[QoSMetrics]) -> float:
        """Calculate resource utilization efficiency score"""
        if not qos_metrics:
            return 0.0
        
        # Analyze response time vs throughput correlation
        response_times = [m.response_time_p95 for m in qos_metrics]
        throughputs = [m.throughput_rps for m in qos_metrics]
        
        # Calculate efficiency (higher throughput with lower response time = better efficiency)
        efficiency_scores = []
        for i in range(len(qos_metrics)):
            if response_times[i] > 0:
                efficiency = throughputs[i] / response_times[i]
                efficiency_scores.append(efficiency)
        
        if efficiency_scores:
            avg_efficiency = statistics.mean(efficiency_scores)
            # Normalize to 0-100 scale
            return min(100, avg_efficiency * 1000)
        else:
            return 0.0
    
    def _detect_anomalies(self, qos_metrics: List[QoSMetrics]) -> List[str]:
        """Detect anomalies in QoS metrics"""
        anomalies = []
        
        if len(qos_metrics) < 3:
            return anomalies
        
        # Calculate moving averages and detect outliers
        response_times = [m.response_time_p95 for m in qos_metrics]
        error_rates = [m.error_rate for m in qos_metrics]
        availability = [m.availability_percent for m in qos_metrics]
        
        # Detect response time spikes
        if len(response_times) >= 3:
            avg_response_time = statistics.mean(response_times)
            std_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            for i, rt in enumerate(response_times):
                if std_response_time > 0 and abs(rt - avg_response_time) > 2 * std_response_time:
                    anomalies.append(f"Response time spike at {qos_metrics[i].timestamp}")
        
        # Detect error rate spikes
        if len(error_rates) >= 3:
            avg_error_rate = statistics.mean(error_rates)
            for i, er in enumerate(error_rates):
                if er > avg_error_rate * 3:  # 3x increase
                    anomalies.append(f"Error rate spike at {qos_metrics[i].timestamp}")
        
        # Detect availability drops
        for i, av in enumerate(availability):
            if av < 95.0:  # Below 95% availability
                anomalies.append(f"Low availability at {qos_metrics[i].timestamp}: {av}%")
        
        return anomalies
    
    def _analyze_trends(self, qos_metrics: List[QoSMetrics]) -> Dict[str, Any]:
        """Analyze trends in QoS metrics"""
        if len(qos_metrics) < 2:
            return {"trends": [], "patterns": []}
        
        # Sort by timestamp
        sorted_metrics = sorted(qos_metrics, key=lambda x: x.timestamp)
        
        trends = []
        patterns = []
        
        # Analyze response time trends
        response_times = [m.response_time_p95 for m in sorted_metrics]
        if len(response_times) >= 2:
            if response_times[-1] > response_times[0] * 1.2:
                trends.append("Response time increasing")
            elif response_times[-1] < response_times[0] * 0.8:
                trends.append("Response time improving")
        
        # Analyze error rate trends
        error_rates = [m.error_rate for m in sorted_metrics]
        if len(error_rates) >= 2:
            if error_rates[-1] > error_rates[0] * 1.5:
                trends.append("Error rate increasing")
            elif error_rates[-1] < error_rates[0] * 0.5:
                trends.append("Error rate improving")
        
        # Analyze throughput patterns
        throughputs = [m.throughput_rps for m in sorted_metrics]
        if len(throughputs) >= 3:
            # Check for cyclical patterns
            if len(set(throughputs)) < len(throughputs) * 0.7:
                patterns.append("Throughput shows cyclical patterns")
        
        return {
            "trends": trends,
            "patterns": patterns,
            "metric_count": len(qos_metrics),
            "time_span": (sorted_metrics[-1].timestamp - sorted_metrics[0].timestamp).total_seconds() / 3600
        }
    
    def _identify_critical_issues(self, qos_metrics: List[QoSMetrics]) -> List[str]:
        """Identify critical issues requiring immediate attention"""
        critical_issues = []
        
        for metrics in qos_metrics:
            # Check for critical thresholds
            if metrics.availability_percent < 90.0:
                critical_issues.append(f"Critical: Availability below 90% ({metrics.availability_percent}%)")
            
            if metrics.error_rate > 0.05:  # 5% error rate
                critical_issues.append(f"Critical: High error rate ({metrics.error_rate * 100:.1f}%)")
            
            if metrics.response_time_p95 > 10000:  # 10 seconds
                critical_issues.append(f"Critical: Very high response time ({metrics.response_time_p95}ms)")
        
        return critical_issues
    
    def _identify_optimization_opportunities(self, qos_metrics: List[QoSMetrics]) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        if not qos_metrics:
            return opportunities
        
        avg_availability = statistics.mean([m.availability_percent for m in qos_metrics])
        avg_response_time = statistics.mean([m.response_time_p95 for m in qos_metrics])
        avg_throughput = statistics.mean([m.throughput_rps for m in qos_metrics])
        
        # Identify improvement areas
        if avg_availability < 99.0:
            opportunities.append("Improve availability to 99%+ for better reliability")
        
        if avg_response_time > 2000:  # 2 seconds
            opportunities.append("Optimize response times for better user experience")
        
        if avg_throughput < 100:  # Low throughput
            opportunities.append("Increase throughput capacity for better scalability")
        
        return opportunities
    
    def generate_recommendations(self, qos_analysis: QoSAnalysis, 
                               customer_profile: Dict[str, Any]) -> List[Recommendation]:
        """
        Generate personalized recommendations based on analysis
        
        Args:
            qos_analysis: QoS analysis results
            customer_profile: Customer profile data
            
        Returns:
            List of generated recommendations
        """
        sector = customer_profile.get('sector', 'private')
        use_case = customer_profile.get('use_case_category', 'general')
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        logger.info(f"Generating recommendations for {customer_profile.get('organization_name')} ({sector})")
        
        recommendations = []
        
        # Generate performance recommendations
        if qos_analysis.performance_score < 70:
            recommendations.extend(self._generate_performance_recommendations(
                qos_analysis, customer_profile, sector, use_case
            ))
        
        # Generate reliability recommendations
        if qos_analysis.reliability_score < 80:
            recommendations.extend(self._generate_reliability_recommendations(
                qos_analysis, customer_profile, sector, use_case
            ))
        
        # Generate capacity recommendations
        if qos_analysis.capacity_score < 60:
            recommendations.extend(self._generate_capacity_recommendations(
                qos_analysis, customer_profile, sector, use_case
            ))
        
        # Generate feature adoption recommendations
        if qos_analysis.utilization_score < 50:
            recommendations.extend(self._generate_feature_adoption_recommendations(
                qos_analysis, customer_profile, sector, use_case
            ))
        
        # Prioritize and score recommendations
        recommendations = self._prioritize_recommendations(recommendations, customer_profile, qos_analysis)
        
        # Update metrics
        self.generation_metrics["total_recommendations_generated"] += len(recommendations)
        self.generation_metrics["successful_generations"] += 1
        self.generation_metrics["sectors_processed"].add(sector)
        
        logger.info(f"Generated {len(recommendations)} recommendations for {tenant_id}")
        return recommendations
    
    def _generate_performance_recommendations(self, qos_analysis: QoSAnalysis,
                                           customer_profile: Dict[str, Any],
                                           sector: str, use_case: str) -> List[Recommendation]:
        """Generate performance optimization recommendations"""
        recommendations = []
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        for template in self.recommendation_templates.get('performance', []):
            recommendation = Recommendation(
                recommendation_id=f"{tenant_id}-perf-{len(recommendations)+1}",
                tenant_id=tenant_id,
                recommendation_type="performance",
                priority=self._calculate_priority(qos_analysis.performance_score, sector),
                title=template['title'],
                description=template['description'],
                expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                business_value=self._calculate_business_value("performance", sector, use_case),
                technical_details=template['technical_details'],
                sector_context=self._get_sector_context(sector),
                use_case_context=self._get_use_case_context(use_case),
                confidence_score=self._calculate_confidence(qos_analysis.performance_score),
                created_date=datetime.now()
            )
            recommendations.append(recommendation)
            
            return recommendations
            
    def _generate_reliability_recommendations(self, qos_analysis: QoSAnalysis,
                                           customer_profile: Dict[str, Any],
                                           sector: str, use_case: str) -> List[Recommendation]:
        """Generate reliability improvement recommendations"""
        recommendations = []
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        for template in self.recommendation_templates.get('reliability', []):
            recommendation = Recommendation(
                recommendation_id=f"{tenant_id}-rel-{len(recommendations)+1}",
                tenant_id=tenant_id,
                recommendation_type="reliability",
                priority=self._calculate_priority(qos_analysis.reliability_score, sector),
                title=template['title'],
                description=template['description'],
                expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                business_value=self._calculate_business_value("reliability", sector, use_case),
                technical_details=template['technical_details'],
                sector_context=self._get_sector_context(sector),
                use_case_context=self._get_use_case_context(use_case),
                confidence_score=self._calculate_confidence(qos_analysis.reliability_score),
                created_date=datetime.now()
            )
            recommendations.append(recommendation)
            
            return recommendations
            
    def _generate_capacity_recommendations(self, qos_analysis: QoSAnalysis,
                                        customer_profile: Dict[str, Any],
                                        sector: str, use_case: str) -> List[Recommendation]:
        """Generate capacity optimization recommendations"""
        recommendations = []
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        for template in self.recommendation_templates.get('capacity', []):
            recommendation = Recommendation(
                recommendation_id=f"{tenant_id}-cap-{len(recommendations)+1}",
                tenant_id=tenant_id,
                recommendation_type="capacity",
                priority=self._calculate_priority(qos_analysis.capacity_score, sector),
                title=template['title'],
                description=template['description'],
                expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                business_value=self._calculate_business_value("capacity", sector, use_case),
                technical_details=template['technical_details'],
                sector_context=self._get_sector_context(sector),
                use_case_context=self._get_use_case_context(use_case),
                confidence_score=self._calculate_confidence(qos_analysis.capacity_score),
                created_date=datetime.now()
            )
            recommendations.append(recommendation)
            
            return recommendations
            
    def _generate_feature_adoption_recommendations(self, qos_analysis: QoSAnalysis,
                                                customer_profile: Dict[str, Any],
                                                sector: str, use_case: str) -> List[Recommendation]:
        """Generate feature adoption recommendations"""
        recommendations = []
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        for template in self.recommendation_templates.get('feature_adoption', []):
            recommendation = Recommendation(
                recommendation_id=f"{tenant_id}-feat-{len(recommendations)+1}",
                tenant_id=tenant_id,
                recommendation_type="feature_adoption",
                priority=self._calculate_priority(qos_analysis.utilization_score, sector),
                title=template['title'],
                description=template['description'],
                expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                business_value=self._calculate_business_value("feature_adoption", sector, use_case),
                technical_details=template['technical_details'],
                sector_context=self._get_sector_context(sector),
                use_case_context=self._get_use_case_context(use_case),
                confidence_score=self._calculate_confidence(qos_analysis.utilization_score),
                created_date=datetime.now()
            )
            recommendations.append(recommendation)
            
            return recommendations
            
    def _calculate_priority(self, score: float, sector: str) -> str:
        """Calculate recommendation priority"""
        sector_rules = self.sector_rules.get(sector, {})
        
        # Base priority on score
        if score < 30:
            base_priority = "critical"
        elif score < 50:
            base_priority = "high"
        elif score < 70:
            base_priority = "medium"
        else:
            base_priority = "low"
        
        # Adjust based on sector requirements
        if sector == "healthcare" and base_priority in ["high", "critical"]:
            return "critical"  # Healthcare gets higher priority for critical issues
        elif sector == "government" and base_priority in ["high", "critical"]:
            return "high"  # Government gets consistent high priority
        
        return base_priority
    
    def _calculate_business_value(self, recommendation_type: str, sector: str, use_case: str) -> float:
        """Calculate business value score for recommendation"""
        base_value = {
            "performance": 80.0,
            "reliability": 90.0,
            "capacity": 70.0,
            "feature_adoption": 60.0
        }.get(recommendation_type, 50.0)
        
        # Sector multipliers
        sector_multipliers = {
            "healthcare": 1.2,  # Higher value for healthcare
            "government": 1.1,  # Higher value for government
            "education": 1.0,   # Standard value
            "private": 0.9,     # Slightly lower for private
            "ngo": 0.8          # Lower for NGO
        }
        
        sector_multiplier = sector_multipliers.get(sector, 1.0)
        
        # Use case multipliers
        use_case_multipliers = {
            "citizen_services": 1.2,
            "healthcare_communication": 1.3,
            "educational_content": 1.1,
            "business_automation": 1.0
        }
        
        use_case_multiplier = use_case_multipliers.get(use_case, 1.0)
        
        return base_value * sector_multiplier * use_case_multiplier
    
    def _calculate_confidence(self, score: float) -> float:
        """Calculate confidence score for recommendation"""
        # Higher confidence for more extreme scores
        if score < 30 or score > 90:
            return 0.9
        elif score < 50 or score > 80:
            return 0.8
        else:
            return 0.7
    
    def _get_sector_context(self, sector: str) -> str:
        """Get sector-specific context for recommendations"""
        sector_contexts = {
            "government": "Government sector requires high compliance and accessibility standards",
            "healthcare": "Healthcare sector prioritizes patient safety and accuracy",
            "education": "Education sector focuses on content quality and accessibility",
            "private": "Private sector emphasizes performance and cost efficiency",
            "ngo": "NGO sector values community impact and transparency"
        }
        return sector_contexts.get(sector, "General business context")
    
    def _get_use_case_context(self, use_case: str) -> str:
        """Get use case specific context for recommendations"""
        use_case_contexts = {
            "citizen_services": "Citizen services require high availability and multilingual support",
            "healthcare_communication": "Healthcare communication needs high accuracy and reliability",
            "educational_content": "Educational content requires quality and accessibility",
            "business_automation": "Business automation focuses on efficiency and scalability"
        }
        return use_case_contexts.get(use_case, "General use case context")
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation],
                                  customer_profile: Dict[str, Any],
                                  qos_analysis: QoSAnalysis) -> List[Recommendation]:
        """Prioritize recommendations based on business value and priority"""
        # Sort by business value (descending) and then by priority order
        priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        
        def sort_key(rec):
            return (priority_order.get(rec.priority, 5), -rec.business_value)
        
        return sorted(recommendations, key=sort_key)
    
    def generate_recommendation_report(self, recommendations: List[Recommendation],
                                     qos_analysis: QoSAnalysis,
                                     customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive recommendation report"""
        report = {
            "customer_info": {
                "organization": customer_profile.get('organization_name'),
                "sector": customer_profile.get('sector'),
                "use_case": customer_profile.get('use_case_category'),
                "tenant_id": customer_profile.get('tenant_id')
            },
            "qos_analysis_summary": {
                "performance_score": qos_analysis.performance_score,
                "reliability_score": qos_analysis.reliability_score,
                "capacity_score": qos_analysis.capacity_score,
                "utilization_score": qos_analysis.utilization_score,
                "critical_issues_count": len(qos_analysis.critical_issues),
                "anomalies_count": len(qos_analysis.anomaly_flags)
            },
            "recommendations_summary": {
                "total_recommendations": len(recommendations),
                "by_priority": {},
                "by_type": {},
                "estimated_impact": {}
            },
            "detailed_recommendations": [],
            "implementation_roadmap": {
                "immediate": [],
                "short_term": [],
                "long_term": []
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Categorize recommendations
        for rec in recommendations:
            # Add to detailed list
            report["detailed_recommendations"].append({
                "id": rec.recommendation_id,
                "title": rec.title,
                "priority": rec.priority,
                "type": rec.recommendation_type,
                "business_value": rec.business_value,
                "expected_impact": rec.expected_impact,
                "implementation_effort": rec.implementation_effort,
                "confidence_score": rec.confidence_score
            })
            
            # Count by priority
            priority = rec.priority
            report["recommendations_summary"]["by_priority"][priority] = \
                report["recommendations_summary"]["by_priority"].get(priority, 0) + 1
            
            # Count by type
            rec_type = rec.recommendation_type
            report["recommendations_summary"]["by_type"][rec_type] = \
                report["recommendations_summary"]["by_type"].get(rec_type, 0) + 1
            
            # Categorize by implementation timeline
            if rec.priority == "critical":
                report["implementation_roadmap"]["immediate"].append(rec.recommendation_id)
            elif rec.priority == "high":
                report["implementation_roadmap"]["short_term"].append(rec.recommendation_id)
            else:
                report["implementation_roadmap"]["long_term"].append(rec.recommendation_id)
        
        # Calculate estimated impact
        total_business_value = sum(rec.business_value for rec in recommendations)
        report["recommendations_summary"]["estimated_impact"] = {
            "total_business_value": total_business_value,
            "average_business_value": total_business_value / len(recommendations) if recommendations else 0,
            "high_impact_count": len([r for r in recommendations if r.business_value > 80])
        }
        
        return report
    
    def get_generation_metrics(self) -> Dict[str, Any]:
        """Get recommendation generation metrics"""
        metrics = copy.deepcopy(self.generation_metrics)
        metrics["sectors_processed"] = list(metrics["sectors_processed"])
        metrics["recommendation_types"] = list(metrics["recommendation_types"])
        return metrics


def main():
    """Main function for testing"""
    # Example usage
    generator = RecommendationGenerator()
    
    # Sample QoS metrics
    sample_qos_metrics = [
        QoSMetrics(
            availability_percent=95.5,
            response_time_p95=2500,
            error_rate=0.02,
            throughput_rps=150,
            latency_p95=1800,
            timestamp=datetime.now() - timedelta(hours=1),
            service_type="Translation",
            tenant_id="gov-department-001"
        ),
        QoSMetrics(
            availability_percent=97.2,
            response_time_p95=1800,
            error_rate=0.01,
            throughput_rps=180,
            latency_p95=1200,
            timestamp=datetime.now(),
            service_type="Translation",
            tenant_id="gov-department-001"
        )
    ]
    
    # Sample customer profile
    sample_profile = {
        "tenant_id": "gov-department-001",
        "organization_name": "Ministry of Digital Services",
        "sector": "government",
        "use_case_category": "citizen_services",
        "target_user_base": 1000000,
        "sla_tier": "premium"
    }
    
    # Analyze QoS metrics
    qos_analysis = generator.analyze_qos_metrics(sample_qos_metrics)
    print(f"QoS Analysis - Performance: {qos_analysis.performance_score:.1f}, "
          f"Reliability: {qos_analysis.reliability_score:.1f}")
    
    # Generate recommendations
    recommendations = generator.generate_recommendations(qos_analysis, sample_profile)
    print(f"Generated {len(recommendations)} recommendations")
    
    # Generate report
    report = generator.generate_recommendation_report(recommendations, qos_analysis, sample_profile)
    print(f"Report generated for {report['customer_info']['organization']}")
    
    # Show metrics
    metrics = generator.get_generation_metrics()
    print(f"Generation metrics: {metrics}")


if __name__ == "__main__":
    main()
