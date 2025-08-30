"""
Actionable Intelligence System for Bhashini

This module provides comprehensive recommendation capabilities including:
- Performance optimization recommendations (latency reduction strategies)
- Reliability improvements (error rate mitigation)
- Capacity planning (scaling recommendations)
- Feature adoption (underutilized service suggestions)
- Sector-specific recommendation logic
- Integration with alerting system for critical recommendations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Recommendation:
    """Data model for optimization recommendations"""
    recommendation_id: str
    tenant_id: str
    recommendation_type: str  # performance, reliability, capacity, feature
    priority: str  # critical, high, medium, low
    title: str
    description: str
    expected_impact: str  # high, medium, low
    implementation_effort: str  # high, medium, low
    status: str  # pending, in_progress, implemented, rejected
    created_date: datetime
    implemented_date: Optional[datetime] = None
    confidence_score: float = 0.0  # 0-100
    business_value: float = 0.0  # Estimated value impact
    technical_details: Optional[Dict[str, Any]] = None
    sector_context: Optional[str] = None
    use_case_context: Optional[str] = None

@dataclass
class QoSAnalysis:
    """Data model for QoS analysis results"""
    tenant_id: str
    analysis_date: datetime
    service_type: str
    performance_score: float  # 0-100
    reliability_score: float  # 0-100
    capacity_score: float  # 0-100
    utilization_score: float  # 0-100
    anomaly_detected: bool
    trend_direction: str  # improving, stable, declining
    critical_issues: List[str]
    optimization_opportunities: List[str]

class RecommendationEngine:
    """AI-powered recommendation engine for Bhashini optimization"""
    
    def __init__(self, sector_config_path: str = "config/sector-kpis.yml"):
        self.sector_config_path = Path(sector_config_path)
        self.sector_config = self._load_sector_config()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Recommendation templates by type
        self.recommendation_templates = self._load_recommendation_templates()
        
        # Sector-specific recommendation rules
        self.sector_rules = self._load_sector_rules()
        
        # Use case specific rules
        self.use_case_rules = self._load_use_case_rules()
    
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
    
    def _load_recommendation_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load recommendation templates for different types"""
        return {
            'performance': [
                {
                    'title': 'Optimize Service Latency',
                    'description': 'Service latency is above optimal thresholds, affecting user experience',
                    'expected_impact': 'high',
                    'implementation_effort': 'medium',
                    'technical_details': {
                        'optimization_type': 'latency_reduction',
                        'target_latency': '1000ms',
                        'current_latency': '2000ms'
                    }
                },
                {
                    'title': 'Improve Throughput Capacity',
                    'description': 'Service throughput is below capacity requirements during peak usage',
                    'expected_impact': 'medium',
                    'implementation_effort': 'high',
                    'technical_details': {
                        'optimization_type': 'capacity_scaling',
                        'target_throughput': '500 RPS',
                        'current_throughput': '300 RPS'
                    }
                }
            ],
            'reliability': [
                {
                    'title': 'Reduce Error Rates',
                    'description': 'Error rates are above acceptable thresholds, impacting service reliability',
                    'expected_impact': 'high',
                    'implementation_effort': 'medium',
                    'technical_details': {
                        'optimization_type': 'error_mitigation',
                        'target_error_rate': '0.01',
                        'current_error_rate': '0.05'
                    }
                },
                {
                    'title': 'Improve Service Availability',
                    'description': 'Service availability is below SLA requirements',
                    'expected_impact': 'critical',
                    'implementation_effort': 'high',
                    'technical_details': {
                        'optimization_type': 'availability_improvement',
                        'target_availability': '99.9%',
                        'current_availability': '98.5%'
                    }
                }
            ],
            'capacity': [
                {
                    'title': 'Scale Service Resources',
                    'description': 'Service is approaching capacity limits during peak usage',
                    'expected_impact': 'medium',
                    'implementation_effort': 'high',
                    'technical_details': {
                        'optimization_type': 'resource_scaling',
                        'scaling_type': 'horizontal',
                        'recommended_instances': '3'
                    }
                },
                {
                    'title': 'Optimize Resource Utilization',
                    'description': 'Resource utilization is below optimal levels, indicating over-provisioning',
                    'expected_impact': 'low',
                    'implementation_effort': 'low',
                    'technical_details': {
                        'optimization_type': 'resource_optimization',
                        'current_utilization': '40%',
                        'target_utilization': '70%'
                    }
                }
            ],
            'feature': [
                {
                    'title': 'Adopt Advanced Features',
                    'description': 'Advanced service features are available but underutilized',
                    'expected_impact': 'medium',
                    'implementation_effort': 'low',
                    'technical_details': {
                        'optimization_type': 'feature_adoption',
                        'feature_name': 'batch_processing',
                        'current_usage': '10%',
                        'potential_usage': '80%'
                    }
                },
                {
                    'title': 'Enable Monitoring Features',
                    'description': 'Enhanced monitoring capabilities can improve operational visibility',
                    'expected_impact': 'low',
                    'implementation_effort': 'low',
                    'technical_details': {
                        'optimization_type': 'monitoring_enhancement',
                        'feature_name': 'real_time_alerting',
                        'current_status': 'disabled'
                    }
                }
            ]
        }
    
    def _load_sector_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load sector-specific recommendation rules"""
        return {
            'government': {
                'priority_multipliers': {
                    'availability': 2.0,      # Critical for public services
                    'compliance': 1.8,        # Important for regulations
                    'cost_efficiency': 1.5,   # Public budget constraints
                    'user_experience': 1.3    # Citizen satisfaction
                },
                'critical_thresholds': {
                    'availability': 99.5,     # Higher availability required
                    'error_rate': 0.01,       # Lower error tolerance
                    'response_time': 2000     # Acceptable response time
                },
                'recommendation_focus': ['reliability', 'compliance', 'availability']
            },
            'healthcare': {
                'priority_multipliers': {
                    'accuracy': 3.0,          # Critical for patient safety
                    'reliability': 2.5,       # Critical for medical services
                    'response_time': 2.0,     # Important for emergency situations
                    'availability': 2.0       # Critical for patient care
                },
                'critical_thresholds': {
                    'availability': 99.9,     # Very high availability required
                    'error_rate': 0.005,      # Very low error tolerance
                    'response_time': 1000     # Fast response required
                },
                'recommendation_focus': ['reliability', 'accuracy', 'response_time']
            },
            'education': {
                'priority_multipliers': {
                    'accessibility': 2.0,     # Important for learning equity
                    'content_quality': 1.8,   # Important for learning outcomes
                    'user_experience': 1.5,   # Important for student engagement
                    'cost_efficiency': 1.3    # Budget considerations
                },
                'critical_thresholds': {
                    'availability': 98.0,     # Good availability required
                    'error_rate': 0.02,       # Moderate error tolerance
                    'response_time': 3000     # Acceptable response time
                },
                'recommendation_focus': ['accessibility', 'content_quality', 'user_experience']
            },
            'private': {
                'priority_multipliers': {
                    'cost_efficiency': 1.8,   # Business cost optimization
                    'user_experience': 1.5,   # Customer satisfaction
                    'reliability': 1.3,       # Service quality
                    'scalability': 1.2        # Business growth
                },
                'critical_thresholds': {
                    'availability': 99.0,     # Good availability required
                    'error_rate': 0.03,       # Moderate error tolerance
                    'response_time': 2500     # Acceptable response time
                },
                'recommendation_focus': ['cost_efficiency', 'scalability', 'user_experience']
            },
            'NGO': {
                'priority_multipliers': {
                    'cost_efficiency': 2.0,   # Limited budget constraints
                    'accessibility': 1.8,     # Mission-driven accessibility
                    'reliability': 1.5,       # Service quality
                    'user_experience': 1.3    # Beneficiary satisfaction
                },
                'critical_thresholds': {
                    'availability': 97.0,     # Basic availability required
                    'error_rate': 0.05,       # Higher error tolerance
                    'response_time': 4000     # Acceptable response time
                },
                'recommendation_focus': ['cost_efficiency', 'accessibility', 'reliability']
            }
        }
    
    def _load_use_case_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load use case specific recommendation rules"""
        return {
            'citizen_services': {
                'priority_factors': ['availability', 'compliance', 'user_experience'],
                'critical_metrics': ['response_time', 'error_rate', 'availability'],
                'optimization_focus': 'public_service_efficiency'
            },
            'patient_communication': {
                'priority_factors': ['accuracy', 'reliability', 'response_time'],
                'critical_metrics': ['error_rate', 'availability', 'latency'],
                'optimization_focus': 'patient_safety'
            },
            'content_localization': {
                'priority_factors': ['content_quality', 'accessibility', 'user_experience'],
                'critical_metrics': ['translation_accuracy', 'response_time', 'availability'],
                'optimization_focus': 'learning_effectiveness'
            },
            'business_operations': {
                'priority_factors': ['cost_efficiency', 'scalability', 'reliability'],
                'critical_metrics': ['throughput', 'error_rate', 'availability'],
                'optimization_focus': 'operational_efficiency'
            },
            'community_services': {
                'priority_factors': ['accessibility', 'cost_efficiency', 'reliability'],
                'critical_metrics': ['availability', 'response_time', 'error_rate'],
                'optimization_focus': 'community_impact'
            }
        }
    
    def analyze_qos_metrics(self, tenant_id: str, qos_metrics: List[Dict[str, Any]]) -> QoSAnalysis:
        """Analyze QoS metrics and identify optimization opportunities"""
        try:
            if not qos_metrics:
                return QoSAnalysis(
                    tenant_id=tenant_id,
                    analysis_date=datetime.now(),
                    service_type='unknown',
                    performance_score=0.0,
                    reliability_score=0.0,
                    capacity_score=0.0,
                    utilization_score=0.0,
                    anomaly_detected=False,
                    trend_direction='stable',
                    critical_issues=[],
                    optimization_opportunities=[]
                )
            
            # Extract metrics for analysis
            latencies = [m.get('latency_ms', 0) for m in qos_metrics]
            throughputs = [m.get('throughput_rps', 0) for m in qos_metrics]
            error_rates = [m.get('error_rate', 0) for m in qos_metrics]
            availabilities = [m.get('availability_percent', 0) for m in qos_metrics]
            
            # Calculate performance scores
            performance_score = self._calculate_performance_score(latencies, throughputs)
            reliability_score = self._calculate_reliability_score(error_rates, availabilities)
            capacity_score = self._calculate_capacity_score(throughputs, availabilities)
            utilization_score = self._calculate_utilization_score(qos_metrics)
            
            # Detect anomalies
            anomaly_detected = self._detect_anomalies(qos_metrics)
            
            # Analyze trends
            trend_direction = self._analyze_trends(qos_metrics)
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(qos_metrics)
            
            # Identify optimization opportunities
            optimization_opportunities = self._identify_optimization_opportunities(qos_metrics)
            
            return QoSAnalysis(
                tenant_id=tenant_id,
                analysis_date=datetime.now(),
                service_type=qos_metrics[0].get('service_type', 'unknown'),
                performance_score=performance_score,
                reliability_score=reliability_score,
                capacity_score=capacity_score,
                utilization_score=utilization_score,
                anomaly_detected=anomaly_detected,
                trend_direction=trend_direction,
                critical_issues=critical_issues,
                optimization_opportunities=optimization_opportunities
            )
            
        except Exception as e:
            logger.error(f"Error analyzing QoS metrics: {e}")
            raise
    
    def _calculate_performance_score(self, latencies: List[float], throughputs: List[float]) -> float:
        """Calculate performance score based on latency and throughput"""
        try:
            if not latencies or not throughputs:
                return 0.0
            
            # Normalize latency (lower is better)
            avg_latency = np.mean(latencies)
            latency_score = max(0, 100 - (avg_latency / 50))  # 5s = 0, 0s = 100
            
            # Normalize throughput (higher is better)
            avg_throughput = np.mean(throughputs)
            throughput_score = min(100, (avg_throughput / 10))  # 1000 RPS = 100
            
            # Weighted average
            performance_score = (latency_score * 0.6 + throughput_score * 0.4)
            
            return max(0, min(100, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50.0
    
    def _calculate_reliability_score(self, error_rates: List[float], availabilities: List[float]) -> float:
        """Calculate reliability score based on error rates and availability"""
        try:
            if not error_rates or not availabilities:
                return 0.0
            
            # Normalize error rate (lower is better)
            avg_error_rate = np.mean(error_rates)
            error_score = max(0, 100 - (avg_error_rate * 2000))  # 5% = 0, 0% = 100
            
            # Normalize availability (higher is better)
            avg_availability = np.mean(availabilities)
            availability_score = avg_availability  # Already 0-100
            
            # Weighted average
            reliability_score = (error_score * 0.7 + availability_score * 0.3)
            
            return max(0, min(100, reliability_score))
            
        except Exception as e:
            logger.error(f"Error calculating reliability score: {e}")
            return 50.0
    
    def _calculate_capacity_score(self, throughputs: List[float], availabilities: List[float]) -> float:
        """Calculate capacity score based on throughput and availability"""
        try:
            if not throughputs or not availabilities:
                return 0.0
            
            # Normalize throughput (higher is better)
            avg_throughput = np.mean(throughputs)
            throughput_score = min(100, (avg_throughput / 5))  # 500 RPS = 100
            
            # Normalize availability (higher is better)
            avg_availability = np.mean(availabilities)
            availability_score = avg_availability  # Already 0-100
            
            # Weighted average
            capacity_score = (throughput_score * 0.6 + availability_score * 0.4)
            
            return max(0, min(100, capacity_score))
            
        except Exception as e:
            logger.error(f"Error calculating capacity score: {e}")
            return 50.0
    
    def _calculate_utilization_score(self, qos_metrics: List[Dict[str, Any]]) -> float:
        """Calculate utilization score based on resource usage patterns"""
        try:
            if not qos_metrics:
                return 0.0
            
            # Calculate utilization based on throughput vs capacity
            throughputs = [m.get('throughput_rps', 0) for m in qos_metrics]
            avg_throughput = np.mean(throughputs)
            
            # Assume optimal utilization is around 70%
            optimal_utilization = 70.0
            current_utilization = min(100, (avg_throughput / 3.5) * 100)  # 350 RPS = 100%
            
            # Score based on proximity to optimal utilization
            utilization_score = 100 - abs(current_utilization - optimal_utilization)
            
            return max(0, min(100, utilization_score))
            
        except Exception as e:
            logger.error(f"Error calculating utilization score: {e}")
            return 50.0
    
    def _detect_anomalies(self, qos_metrics: List[Dict[str, Any]]) -> bool:
        """Detect anomalies in QoS metrics using isolation forest"""
        try:
            if len(qos_metrics) < 10:
                return False
            
            # Extract numerical features for anomaly detection
            features = []
            for metric in qos_metrics:
                feature_vector = [
                    metric.get('latency_ms', 0),
                    metric.get('throughput_rps', 0),
                    metric.get('error_rate', 0),
                    metric.get('availability_percent', 0)
                ]
                features.append(feature_vector)
            
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Detect anomalies
            anomaly_labels = self.anomaly_detector.fit_predict(features_scaled)
            
            # Check if any anomalies were detected
            anomalies_detected = any(label == -1 for label in anomaly_labels)
            
            return anomalies_detected
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return False
    
    def _analyze_trends(self, qos_metrics: List[Dict[str, Any]]) -> str:
        """Analyze trends in QoS metrics over time"""
        try:
            if len(qos_metrics) < 5:
                return 'stable'
            
            # Extract performance metrics over time
            latencies = [m.get('latency_ms', 0) for m in qos_metrics]
            error_rates = [m.get('error_rate', 0) for m in qos_metrics]
            
            # Calculate trend indicators
            latency_trend = np.polyfit(range(len(latencies)), latencies, 1)[0]
            error_trend = np.polyfit(range(len(error_rates)), error_rates, 1)[0]
            
            # Determine overall trend
            if latency_trend < -100 and error_trend < -0.01:
                return 'improving'
            elif latency_trend > 100 or error_trend > 0.01:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return 'stable'
    
    def _identify_critical_issues(self, qos_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify critical issues in QoS metrics"""
        critical_issues = []
        
        try:
            for metric in qos_metrics:
                # Check availability
                if metric.get('availability_percent', 100) < 95:
                    critical_issues.append(f"Low availability: {metric.get('availability_percent', 0)}%")
                
                # Check error rate
                if metric.get('error_rate', 0) > 0.05:
                    critical_issues.append(f"High error rate: {metric.get('error_rate', 0):.3f}")
                
                # Check response time
                if metric.get('latency_ms', 0) > 5000:
                    critical_issues.append(f"High latency: {metric.get('latency_ms', 0)}ms")
                
                # Check throughput
                if metric.get('throughput_rps', 0) < 50:
                    critical_issues.append(f"Low throughput: {metric.get('throughput_rps', 0)} RPS")
            
            return critical_issues
            
        except Exception as e:
            logger.error(f"Error identifying critical issues: {e}")
            return ["Unable to analyze critical issues"]
    
    def _identify_optimization_opportunities(self, qos_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify optimization opportunities in QoS metrics"""
        opportunities = []
        
        try:
            avg_latency = np.mean([m.get('latency_ms', 0) for m in qos_metrics])
            avg_throughput = np.mean([m.get('throughput_rps', 0) for m in qos_metrics])
            avg_error_rate = np.mean([m.get('error_rate', 0) for m in qos_metrics])
            
            if avg_latency > 2000:
                opportunities.append("Optimize service latency for better user experience")
            
            if avg_throughput < 200:
                opportunities.append("Scale service capacity for higher throughput")
            
            if avg_error_rate > 0.02:
                opportunities.append("Implement error handling improvements")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {e}")
            return ["Unable to analyze optimization opportunities"]
    
    def generate_recommendations(self, qos_analysis: QoSAnalysis, 
                               customer_profile: Dict[str, Any]) -> List[Recommendation]:
        """Generate personalized recommendations based on QoS analysis and customer profile"""
        try:
            recommendations = []
            sector = customer_profile.get('sector', 'private')
            use_case = customer_profile.get('use_case_category', 'business_operations')
            
            # Get sector and use case rules
            sector_rule = self.sector_rules.get(sector, self.sector_rules['private'])
            use_case_rule = self.use_case_rules.get(use_case, self.use_case_rules['business_operations'])
            
            # Generate performance recommendations
            if qos_analysis.performance_score < 70:
                recommendations.extend(self._generate_performance_recommendations(
                    qos_analysis, customer_profile, sector_rule, use_case_rule
                ))
            
            # Generate reliability recommendations
            if qos_analysis.reliability_score < 80:
                recommendations.extend(self._generate_reliability_recommendations(
                    qos_analysis, customer_profile, sector_rule, use_case_rule
                ))
            
            # Generate capacity recommendations
            if qos_analysis.capacity_score < 75:
                recommendations.extend(self._generate_capacity_recommendations(
                    qos_analysis, customer_profile, sector_rule, use_case_rule
                ))
            
            # Generate feature recommendations
            if qos_analysis.utilization_score < 60:
                recommendations.extend(self._generate_feature_recommendations(
                    qos_analysis, customer_profile, sector_rule, use_case_rule
                ))
            
            # Prioritize and score recommendations
            recommendations = self._prioritize_recommendations(recommendations, sector_rule, use_case_rule)
            
            # Limit to top recommendations
            max_recommendations = 5
            if len(recommendations) > max_recommendations:
                recommendations = recommendations[:max_recommendations]
            
            logger.info(f"Generated {len(recommendations)} recommendations for tenant {qos_analysis.tenant_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_performance_recommendations(self, qos_analysis: QoSAnalysis,
                                            customer_profile: Dict[str, Any],
                                            sector_rule: Dict[str, Any],
                                            use_case_rule: Dict[str, Any]) -> List[Recommendation]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        try:
            templates = self.recommendation_templates['performance']
            
            for template in templates:
                # Calculate priority based on sector rules
                priority = self._calculate_priority('performance', template, sector_rule, use_case_rule)
            
            # Calculate expected impact
                impact = self._calculate_impact(qos_analysis.performance_score, template['expected_impact'])
                
                # Calculate implementation effort
                effort = self._calculate_effort(template['implementation_effort'])
            
            # Calculate confidence score
                confidence = self._calculate_confidence(qos_analysis, customer_profile)
            
                # Calculate business value
                business_value = self._calculate_business_value(impact, effort, customer_profile)
                
            recommendation = Recommendation(
                    recommendation_id=f"perf_{qos_analysis.tenant_id}_{len(recommendations)}",
                    tenant_id=qos_analysis.tenant_id,
                recommendation_type='performance',
                priority=priority,
                title=template['title'],
                description=template['description'],
                    expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                status='pending',
                created_date=datetime.now(),
                    confidence_score=confidence,
                    business_value=business_value,
                    technical_details=template.get('technical_details'),
                    sector_context=customer_profile.get('sector'),
                    use_case_context=customer_profile.get('use_case_category')
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating performance recommendations: {e}")
            return []
    
    def _generate_reliability_recommendations(self, qos_analysis: QoSAnalysis,
                                            customer_profile: Dict[str, Any],
                                            sector_rule: Dict[str, Any],
                                            use_case_rule: Dict[str, Any]) -> List[Recommendation]:
        """Generate reliability improvement recommendations"""
        recommendations = []
        
        try:
            templates = self.recommendation_templates['reliability']
            
            for template in templates:
                # Calculate priority based on sector rules
                priority = self._calculate_priority('reliability', template, sector_rule, use_case_rule)
            
            # Calculate expected impact
                impact = self._calculate_impact(qos_analysis.reliability_score, template['expected_impact'])
                
                # Calculate implementation effort
                effort = self._calculate_effort(template['implementation_effort'])
            
            # Calculate confidence score
                confidence = self._calculate_confidence(qos_analysis, customer_profile)
            
                # Calculate business value
                business_value = self._calculate_business_value(impact, effort, customer_profile)
                
            recommendation = Recommendation(
                    recommendation_id=f"rel_{qos_analysis.tenant_id}_{len(recommendations)}",
                    tenant_id=qos_analysis.tenant_id,
                recommendation_type='reliability',
                priority=priority,
                title=template['title'],
                description=template['description'],
                    expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                status='pending',
                created_date=datetime.now(),
                    confidence_score=confidence,
                    business_value=business_value,
                    technical_details=template.get('technical_details'),
                    sector_context=customer_profile.get('sector'),
                    use_case_context=customer_profile.get('use_case_category')
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating reliability recommendations: {e}")
            return []
    
    def _generate_capacity_recommendations(self, qos_analysis: QoSAnalysis,
                                         customer_profile: Dict[str, Any],
                                         sector_rule: Dict[str, Any],
                                         use_case_rule: Dict[str, Any]) -> List[Recommendation]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        try:
            templates = self.recommendation_templates['capacity']
            
            for template in templates:
                # Calculate priority based on sector rules
                priority = self._calculate_priority('capacity', template, sector_rule, use_case_rule)
            
            # Calculate expected impact
                impact = self._calculate_impact(qos_analysis.capacity_score, template['expected_impact'])
                
                # Calculate implementation effort
                effort = self._calculate_effort(template['implementation_effort'])
            
            # Calculate confidence score
                confidence = self._calculate_confidence(qos_analysis, customer_profile)
            
                # Calculate business value
                business_value = self._calculate_business_value(impact, effort, customer_profile)
                
            recommendation = Recommendation(
                    recommendation_id=f"cap_{qos_analysis.tenant_id}_{len(recommendations)}",
                    tenant_id=qos_analysis.tenant_id,
                recommendation_type='capacity',
                title=template['title'],
                description=template['description'],
                    expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                status='pending',
                created_date=datetime.now(),
                    priority=priority,
                    confidence_score=confidence,
                    business_value=business_value,
                    technical_details=template.get('technical_details'),
                    sector_context=customer_profile.get('sector'),
                    use_case_context=customer_profile.get('use_case_category')
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating capacity recommendations: {e}")
            return []
    
    def _generate_feature_recommendations(self, qos_analysis: QoSAnalysis,
                                        customer_profile: Dict[str, Any],
                                        sector_rule: Dict[str, Any],
                                        use_case_rule: Dict[str, Any]) -> List[Recommendation]:
        """Generate feature adoption recommendations"""
        recommendations = []
        
        try:
            templates = self.recommendation_templates['feature']
            
            for template in templates:
                # Calculate priority based on sector rules
                priority = self._calculate_priority('feature', template, sector_rule, use_case_rule)
            
            # Calculate expected impact
                impact = self._calculate_impact(qos_analysis.utilization_score, template['expected_impact'])
                
                # Calculate implementation effort
                effort = self._calculate_effort(template['implementation_effort'])
            
            # Calculate confidence score
                confidence = self._calculate_confidence(qos_analysis, customer_profile)
            
                # Calculate business value
                business_value = self._calculate_business_value(impact, effort, customer_profile)
                
            recommendation = Recommendation(
                    recommendation_id=f"feat_{qos_analysis.tenant_id}_{len(recommendations)}",
                    tenant_id=qos_analysis.tenant_id,
                recommendation_type='feature',
                priority=priority,
                title=template['title'],
                description=template['description'],
                    expected_impact=template['expected_impact'],
                implementation_effort=template['implementation_effort'],
                status='pending',
                created_date=datetime.now(),
                    confidence_score=confidence,
                    business_value=business_value,
                    technical_details=template.get('technical_details'),
                    sector_context=customer_profile.get('sector'),
                    use_case_context=customer_profile.get('use_case_category')
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating feature recommendations: {e}")
            return []
    
    def _calculate_priority(self, rec_type: str, template: Dict[str, Any],
                           sector_rule: Dict[str, Any], use_case_rule: Dict[str, Any]) -> str:
        """Calculate recommendation priority based on sector and use case rules"""
        try:
            # Base priority from template
            base_priority = template['expected_impact']
            
            # Apply sector multipliers
            sector_multiplier = 1.0
            if rec_type in sector_rule.get('priority_multipliers', {}):
                sector_multiplier = sector_rule['priority_multipliers'][rec_type]
            
            # Apply use case focus
            use_case_focus = use_case_rule.get('priority_factors', [])
            use_case_multiplier = 1.5 if rec_type in use_case_focus else 1.0
            
            # Calculate final priority
            priority_score = 0
            if base_priority == 'critical':
                priority_score = 100
            elif base_priority == 'high':
                priority_score = 75
            elif base_priority == 'medium':
                priority_score = 50
            else:
                priority_score = 25
            
            # Apply multipliers
            final_score = priority_score * sector_multiplier * use_case_multiplier
            
            # Convert to priority string
            if final_score >= 100:
                return 'critical'
            elif final_score >= 75:
                return 'high'
            elif final_score >= 50:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 'medium'
    
    def _calculate_impact(self, current_score: float, expected_impact: str) -> float:
        """Calculate expected impact score"""
        try:
            impact_scores = {
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }
            
            base_impact = impact_scores.get(expected_impact, 0.5)
            
            # Adjust impact based on current performance
            if current_score < 50:
                return base_impact * 1.5  # Higher impact for poor performance
            elif current_score < 75:
                return base_impact * 1.2  # Moderate impact for average performance
                else:
                return base_impact * 0.8  # Lower impact for good performance
            
        except Exception as e:
            logger.error(f"Error calculating impact: {e}")
            return 0.5
    
    def _calculate_effort(self, implementation_effort: str) -> float:
        """Calculate implementation effort score"""
        try:
            effort_scores = {
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }
            
            return effort_scores.get(implementation_effort, 0.5)
                
        except Exception as e:
            logger.error(f"Error calculating effort: {e}")
            return 0.5
    
    def _calculate_confidence(self, qos_analysis: QoSAnalysis, customer_profile: Dict[str, Any]) -> float:
        """Calculate confidence score for recommendations"""
        try:
            confidence = 70.0  # Base confidence
            
            # Increase confidence based on data quality
            if qos_analysis.anomaly_detected:
                confidence += 10  # Anomalies provide clear signals
            
            # Increase confidence based on profile completeness
            required_fields = ['sector', 'use_case_category', 'sla_tier']
            complete_fields = sum(1 for field in required_fields if customer_profile.get(field))
            profile_completeness = complete_fields / len(required_fields)
            confidence += profile_completeness * 15
            
            # Ensure confidence is within 0-100 range
            confidence = max(0, min(100, confidence))
            
            return confidence
                
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 50.0
    
    def _calculate_business_value(self, impact: float, effort: float, 
                                customer_profile: Dict[str, Any]) -> float:
        """Calculate business value score for recommendations"""
        try:
            # Base value calculation
            base_value = impact * (1 - effort)  # Higher impact, lower effort = higher value
            
            # Apply sector multiplier
            sector = customer_profile.get('sector', 'private')
            sector_multipliers = {
                'government': 1.5,
                'healthcare': 2.0,
                'education': 1.8,
                'NGO': 1.3,
                'private': 1.0
            }
            
            sector_multiplier = sector_multipliers.get(sector, 1.0)
            
            # Calculate final business value
            business_value = base_value * sector_multiplier * 100  # Scale to 0-100
            
            return max(0, min(100, business_value))
            
        except Exception as e:
            logger.error(f"Error calculating business value: {e}")
            return 50.0
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation],
                                  sector_rule: Dict[str, Any], use_case_rule: Dict[str, Any]) -> List[Recommendation]:
        """Prioritize recommendations based on business value and implementation effort"""
        try:
            # Sort by priority (critical > high > medium > low)
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            
            def sort_key(rec):
                priority_score = priority_order.get(rec.priority, 0)
                # Secondary sort by business value (higher is better)
                return (-priority_score, -rec.business_value)
            
            sorted_recommendations = sorted(recommendations, key=sort_key)
            
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"Error prioritizing recommendations: {e}")
            return recommendations
    
    def generate_recommendation_report(self, recommendations: List[Recommendation],
                                    qos_analysis: QoSAnalysis,
                                    customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive recommendation report"""
        try:
            report = {
                'executive_summary': {
                    'total_recommendations': len(recommendations),
                    'critical_recommendations': len([r for r in recommendations if r.priority == 'critical']),
                    'high_priority_recommendations': len([r for r in recommendations if r.priority == 'high']),
                    'estimated_business_value': sum(r.business_value for r in recommendations)
                },
                'qos_analysis_summary': {
                    'performance_score': f"{qos_analysis.performance_score:.1f}/100",
                    'reliability_score': f"{qos_analysis.reliability_score:.1f}/100",
                    'capacity_score': f"{qos_analysis.capacity_score:.1f}/100",
                    'utilization_score': f"{qos_analysis.utilization_score:.1f}/100",
                    'trend_direction': qos_analysis.trend_direction,
                    'anomalies_detected': qos_analysis.anomaly_detected
                },
                'recommendations': [
                    {
                        'id': rec.recommendation_id,
                        'type': rec.recommendation_type,
                        'priority': rec.priority,
                        'title': rec.title,
                        'description': rec.description,
                        'expected_impact': rec.expected_impact,
                        'implementation_effort': rec.implementation_effort,
                        'business_value': f"{rec.business_value:.1f}/100",
                        'confidence': f"{rec.confidence_score:.1f}%",
                        'technical_details': rec.technical_details
                    }
                    for rec in recommendations
                ],
                'customer_context': {
                    'sector': customer_profile.get('sector', 'Unknown'),
                    'use_case': customer_profile.get('use_case_category', 'Unknown'),
                    'sla_tier': customer_profile.get('sla_tier', 'Unknown')
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating recommendation report: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    # Initialize recommendation engine
    engine = RecommendationEngine()
    
    # Sample QoS metrics
    qos_metrics = [
        {
            'service_type': 'translation',
            'latency_ms': 2500,
            'throughput_rps': 150,
            'error_rate': 0.03,
            'availability_percent': 98.5
        },
        {
            'service_type': 'tts',
            'latency_ms': 1800,
            'throughput_rps': 120,
            'error_rate': 0.02,
            'availability_percent': 99.0
        }
    ]
    
    # Sample customer profile
    customer_profile = {
        'tenant_id': 'gov_digital_india',
        'sector': 'government',
        'use_case_category': 'citizen_services',
        'sla_tier': 'premium'
    }
    
    # Analyze QoS metrics
    try:
        qos_analysis = engine.analyze_qos_metrics('gov_digital_india', qos_metrics)
        
        print("QoS Analysis Results:")
        print(f"Performance Score: {qos_analysis.performance_score:.1f}/100")
        print(f"Reliability Score: {qos_analysis.reliability_score:.1f}/100")
        print(f"Capacity Score: {qos_analysis.capacity_score:.1f}/100")
        print(f"Utilization Score: {qos_analysis.utilization_score:.1f}/100")
        print(f"Anomaly Detected: {qos_analysis.anomaly_detected}")
        print(f"Trend Direction: {qos_analysis.trend_direction}")
        print(f"Critical Issues: {qos_analysis.critical_issues}")
        print(f"Optimization Opportunities: {qos_analysis.optimization_opportunities}")
    
    # Generate recommendations
        recommendations = engine.generate_recommendations(qos_analysis, customer_profile)
    
        print(f"\nGenerated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.title} ({rec.priority} priority)")
            print(f"   Type: {rec.recommendation_type}")
            print(f"   Impact: {rec.expected_impact}")
            print(f"   Effort: {rec.implementation_effort}")
            print(f"   Business Value: {rec.business_value:.1f}/100")
            print(f"   Confidence: {rec.confidence_score:.1f}%")
            print()
        
        # Generate report
        report = engine.generate_recommendation_report(recommendations, qos_analysis, customer_profile)
        print("Recommendation Report Generated Successfully")
        
    except Exception as e:
        print(f"Error in recommendation generation: {e}")
