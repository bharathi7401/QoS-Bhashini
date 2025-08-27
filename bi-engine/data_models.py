"""
Data Models for Bhashini Business Intelligence System

This module provides comprehensive data models including:
- SQLAlchemy models for customer profile storage
- Value estimation models for impact scores and ROI metrics
- Recommendation models with prioritization and tracking
- Data validation schemas using Pydantic
- Database migration utilities
- Data serialization and transformation functions
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import text
from pydantic import BaseModel, Field, validator
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

# Pydantic models for API validation
class CustomerProfileCreate(BaseModel):
    """Pydantic model for creating customer profiles"""
    organization_name: str = Field(..., min_length=1, max_length=200)
    sector: str = Field(..., regex="^(government|healthcare|education|private|NGO)$")
    use_case_category: str = Field(..., min_length=1, max_length=100)
    specific_use_cases: List[str] = Field(default_factory=list)
    target_user_base: int = Field(..., gt=0)
    geographical_coverage: List[str] = Field(default_factory=list)
    languages_required: List[str] = Field(default_factory=list)
    business_goals: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    sla_tier: str = Field(..., regex="^(premium|standard|basic)$")
    contact_email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = Field(None, gt=0)
    employee_count: Optional[int] = Field(None, gt=0)
    
    @validator('target_user_base')
    def validate_user_base(cls, v):
        if v > 100000000:  # 100M users max
            raise ValueError('Target user base too large')
        return v
    
    @validator('annual_revenue')
    def validate_revenue(cls, v):
        if v is not None and v > 1000000000000:  # 1T revenue max
            raise ValueError('Annual revenue too large')
        return v

class CustomerProfileUpdate(BaseModel):
    """Pydantic model for updating customer profiles"""
    organization_name: Optional[str] = Field(None, min_length=1, max_length=200)
    sector: Optional[str] = Field(None, regex="^(government|healthcare|education|private|NGO)$")
    use_case_category: Optional[str] = Field(None, min_length=1, max_length=100)
    specific_use_cases: Optional[List[str]] = None
    target_user_base: Optional[int] = Field(None, gt=0)
    geographical_coverage: Optional[List[str]] = None
    languages_required: Optional[List[str]] = None
    business_goals: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    sla_tier: Optional[str] = Field(None, regex="^(premium|standard|basic)$")
    contact_email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = Field(None, gt=0)
    employee_count: Optional[int] = Field(None, gt=0)
    profile_status: Optional[str] = Field(None, regex="^(active|inactive|pending)$")

class ValueEstimateCreate(BaseModel):
    """Pydantic model for creating value estimates"""
    tenant_id: str = Field(..., min_length=1)
    cost_savings: float = Field(..., ge=0)
    user_reach_impact: int = Field(..., ge=0)
    efficiency_gains: float = Field(..., ge=0, le=100)
    quality_improvements: float = Field(..., ge=0, le=100)
    calculation_methodology: str = Field(..., min_length=1)
    sector_multiplier: float = Field(..., gt=0)
    use_case_multiplier: float = Field(..., gt=0)
    confidence_score: float = Field(..., ge=0, le=100)
    roi_ratio: float = Field(..., ge=0)
    payback_period_months: float = Field(..., ge=0)

class RecommendationCreate(BaseModel):
    """Pydantic model for creating recommendations"""
    tenant_id: str = Field(..., min_length=1)
    recommendation_type: str = Field(..., regex="^(performance|reliability|capacity|feature)$")
    priority: str = Field(..., regex="^(critical|high|medium|low)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    expected_impact: str = Field(..., regex="^(high|medium|low)$")
    implementation_effort: str = Field(..., regex="^(high|medium|low)$")
    technical_details: Optional[Dict[str, Any]] = None
    sector_context: Optional[str] = None
    use_case_context: Optional[str] = None

# SQLAlchemy models
class CustomerProfile(Base):
    """SQLAlchemy model for customer profiles"""
    __tablename__ = 'customer_profiles'
    
    tenant_id = Column(String(50), primary_key=True)
    organization_name = Column(String(200), nullable=False)
    sector = Column(String(50), nullable=False, index=True)
    use_case_category = Column(String(100), nullable=False, index=True)
    specific_use_cases = Column(JSON, nullable=False)
    target_user_base = Column(Integer, nullable=False)
    geographical_coverage = Column(JSON, nullable=False)
    languages_required = Column(JSON, nullable=False)
    business_goals = Column(JSON, nullable=False)
    success_metrics = Column(JSON, nullable=False)
    sla_tier = Column(String(20), nullable=False, index=True)
    profile_created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_status = Column(String(20), nullable=False, default='pending', index=True)
    contact_email = Column(String(200), nullable=False)
    contact_phone = Column(String(50))
    industry = Column(String(100))
    annual_revenue = Column(Float)
    employee_count = Column(Integer)
    
    # Relationships
    value_estimates = relationship("ValueEstimate", back_populates="customer_profile")
    recommendations = relationship("Recommendation", back_populates="customer_profile")
    profile_history = relationship("ProfileHistory", back_populates="customer_profile")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['profile_created_date'] = self.profile_created_date.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """Update profile from dictionary"""
        for key, value in updates.items():
            if hasattr(self, key) and key not in ['tenant_id', 'profile_created_date']:
                setattr(self, key, value)
        self.last_updated = datetime.utcnow()

class ValueEstimate(Base):
    """SQLAlchemy model for value estimates"""
    __tablename__ = 'value_estimates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey('customer_profiles.tenant_id'), nullable=False, index=True)
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    cost_savings = Column(Float, nullable=False)
    user_reach_impact = Column(Integer, nullable=False)
    efficiency_gains = Column(Float, nullable=False)
    quality_improvements = Column(Float, nullable=False)
    total_value_score = Column(Float, nullable=False)
    calculation_methodology = Column(String(100), nullable=False)
    sector_multiplier = Column(Float, nullable=False)
    use_case_multiplier = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    roi_ratio = Column(Float, nullable=False)
    payback_period_months = Column(Float, nullable=False)
    
    # Relationships
    customer_profile = relationship("CustomerProfile", back_populates="value_estimates")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert estimate to dictionary"""
        data = asdict(self)
        data['calculation_date'] = self.calculation_date.isoformat()
        return data

class Recommendation(Base):
    """SQLAlchemy model for recommendations"""
    __tablename__ = 'recommendations'
    
    recommendation_id = Column(String(100), primary_key=True)
    tenant_id = Column(String(50), ForeignKey('customer_profiles.tenant_id'), nullable=False, index=True)
    recommendation_type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    expected_impact = Column(String(20), nullable=False)
    implementation_effort = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default='pending', index=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    implemented_date = Column(DateTime)
    confidence_score = Column(Float, nullable=False, default=0.0)
    business_value = Column(Float, nullable=False, default=0.0)
    technical_details = Column(JSON)
    sector_context = Column(String(50))
    use_case_context = Column(String(100))
    
    # Relationships
    customer_profile = relationship("CustomerProfile", back_populates="recommendations")
    implementation_tracking = relationship("ImplementationTracking", back_populates="recommendation", uselist=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary"""
        data = asdict(self)
        data['created_date'] = self.created_date.isoformat()
        if self.implemented_date:
            data['implemented_date'] = self.implemented_date.isoformat()
        return data

class ProfileHistory(Base):
    """SQLAlchemy model for profile change history"""
    __tablename__ = 'profile_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey('customer_profiles.tenant_id'), nullable=False, index=True)
    change_type = Column(String(50), nullable=False)  # created, updated, status_changed
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    changed_by = Column(String(100))  # system, user, api
    
    # Relationships
    customer_profile = relationship("CustomerProfile", back_populates="profile_history")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history record to dictionary"""
        data = asdict(self)
        data['changed_at'] = self.changed_at.isoformat()
        return data

class ImplementationTracking(Base):
    """SQLAlchemy model for recommendation implementation tracking"""
    __tablename__ = 'implementation_tracking'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String(100), ForeignKey('recommendations.recommendation_id'), nullable=False, unique=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    implementation_start_date = Column(DateTime)
    implementation_end_date = Column(DateTime)
    actual_impact = Column(Float)
    actual_cost = Column(Float)
    implementation_notes = Column(Text)
    success_metrics = Column(JSON)
    lessons_learned = Column(Text)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="implementation_tracking")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tracking record to dictionary"""
        data = asdict(self)
        if self.implementation_start_date:
            data['implementation_start_date'] = self.implementation_start_date.isoformat()
        if self.implementation_end_date:
            data['implementation_end_date'] = self.implementation_end_date.isoformat()
        return data

class QoSMetrics(Base):
    """SQLAlchemy model for QoS metrics cache"""
    __tablename__ = 'qos_metrics_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    service_type = Column(String(50), nullable=False)
    latency_ms = Column(Float, nullable=False)
    throughput_rps = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    availability_percent = Column(Float, nullable=False)
    response_time_p95 = Column(Float, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

# Database manager class
class DatabaseManager:
    """Database management class for the BI system"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        session.close()
    
    def execute_migration(self, migration_sql: str) -> bool:
        """Execute database migration"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text(migration_sql))
                connection.commit()
            logger.info("Migration executed successfully")
            return True
        except Exception as e:
            logger.error(f"Error executing migration: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            # This is a simplified backup - in production, use proper backup tools
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM customer_profiles"))
                profiles = [dict(row) for row in result]
                
                with open(backup_path, 'w') as f:
                    json.dump(profiles, f, indent=2, default=str)
            
            logger.info(f"Database backup created at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False

# Data validation and transformation utilities
class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_customer_profile(profile_data: Dict[str, Any]) -> List[str]:
        """Validate customer profile data and return validation errors"""
        errors = []
        
        # Required field validation
        required_fields = ['organization_name', 'sector', 'use_case_category', 'target_user_base']
        for field in required_fields:
            if not profile_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Sector validation
        valid_sectors = ['government', 'healthcare', 'education', 'private', 'NGO']
        if profile_data.get('sector') and profile_data['sector'] not in valid_sectors:
            errors.append(f"Invalid sector. Must be one of: {', '.join(valid_sectors)}")
        
        # Use case validation
        valid_use_cases = [
            'citizen_services', 'healthcare', 'education', 'business_operations',
            'community_services', 'content_localization', 'patient_communication'
        ]
        if profile_data.get('use_case_category') and profile_data['use_case_category'] not in valid_use_cases:
            errors.append(f"Invalid use case category. Must be one of: {', '.join(valid_use_cases)}")
        
        # SLA tier validation
        valid_sla_tiers = ['premium', 'standard', 'basic']
        if profile_data.get('sla_tier') and profile_data['sla_tier'] not in valid_sla_tiers:
            errors.append(f"Invalid SLA tier. Must be one of: {', '.join(valid_sla_tiers)}")
        
        # Numeric validation
        if profile_data.get('target_user_base') and not isinstance(profile_data['target_user_base'], int):
            errors.append("target_user_base must be an integer")
        
        if profile_data.get('target_user_base') and profile_data['target_user_base'] <= 0:
            errors.append("target_user_base must be positive")
        
        # Email validation
        if profile_data.get('contact_email') and '@' not in profile_data['contact_email']:
            errors.append("Invalid contact email format")
        
        return errors
    
    @staticmethod
    def validate_value_estimate(estimate_data: Dict[str, Any]) -> List[str]:
        """Validate value estimate data and return validation errors"""
        errors = []
        
        # Required field validation
        required_fields = ['tenant_id', 'cost_savings', 'user_reach_impact', 'efficiency_gains']
        for field in required_fields:
            if not estimate_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Numeric validation
        if estimate_data.get('cost_savings') and estimate_data['cost_savings'] < 0:
            errors.append("cost_savings must be non-negative")
        
        if estimate_data.get('user_reach_impact') and estimate_data['user_reach_impact'] < 0:
            errors.append("user_reach_impact must be non-negative")
        
        if estimate_data.get('efficiency_gains') and (estimate_data['efficiency_gains'] < 0 or estimate_data['efficiency_gains'] > 100):
            errors.append("efficiency_gains must be between 0 and 100")
        
        if estimate_data.get('quality_improvements') and (estimate_data['quality_improvements'] < 0 or estimate_data['quality_improvements'] > 100):
            errors.append("quality_improvements must be between 0 and 100")
        
        if estimate_data.get('confidence_score') and (estimate_data['confidence_score'] < 0 or estimate_data['confidence_score'] > 100):
            errors.append("confidence_score must be between 0 and 100")
        
        return errors

class DataTransformer:
    """Data transformation utilities"""
    
    @staticmethod
    def profile_to_api_response(profile: CustomerProfile) -> Dict[str, Any]:
        """Transform customer profile to API response format"""
        return {
            'tenant_id': profile.tenant_id,
            'organization_name': profile.organization_name,
            'sector': profile.sector,
            'use_case_category': profile.use_case_category,
            'specific_use_cases': profile.specific_use_cases,
            'target_user_base': profile.target_user_base,
            'geographical_coverage': profile.geographical_coverage,
            'languages_required': profile.languages_required,
            'business_goals': profile.business_goals,
            'success_metrics': profile.success_metrics,
            'sla_tier': profile.sla_tier,
            'profile_status': profile.profile_status,
            'contact_email': profile.contact_email,
            'contact_phone': profile.contact_phone,
            'industry': profile.industry,
            'annual_revenue': profile.annual_revenue,
            'employee_count': profile.employee_count,
            'profile_created_date': profile.profile_created_date.isoformat(),
            'last_updated': profile.last_updated.isoformat()
        }
    
    @staticmethod
    def value_estimate_to_api_response(estimate: ValueEstimate) -> Dict[str, Any]:
        """Transform value estimate to API response format"""
        return {
            'id': estimate.id,
            'tenant_id': estimate.tenant_id,
            'calculation_date': estimate.calculation_date.isoformat(),
            'cost_savings': estimate.cost_savings,
            'user_reach_impact': estimate.user_reach_impact,
            'efficiency_gains': estimate.efficiency_gains,
            'quality_improvements': estimate.quality_improvements,
            'total_value_score': estimate.total_value_score,
            'calculation_methodology': estimate.calculation_methodology,
            'sector_multiplier': estimate.sector_multiplier,
            'use_case_multiplier': estimate.use_case_multiplier,
            'confidence_score': estimate.confidence_score,
            'roi_ratio': estimate.roi_ratio,
            'payback_period_months': estimate.payback_period_months
        }
    
    @staticmethod
    def recommendation_to_api_response(recommendation: Recommendation) -> Dict[str, Any]:
        """Transform recommendation to API response format"""
        return {
            'recommendation_id': recommendation.recommendation_id,
            'tenant_id': recommendation.tenant_id,
            'recommendation_type': recommendation.recommendation_type,
            'priority': recommendation.priority,
            'title': recommendation.title,
            'description': recommendation.description,
            'expected_impact': recommendation.expected_impact,
            'implementation_effort': recommendation.implementation_effort,
            'status': recommendation.status,
            'created_date': recommendation.created_date.isoformat(),
            'implemented_date': recommendation.implemented_date.isoformat() if recommendation.implemented_date else None,
            'confidence_score': recommendation.confidence_score,
            'business_value': recommendation.business_value,
            'technical_details': recommendation.technical_details,
            'sector_context': recommendation.sector_context,
            'use_case_context': recommendation.use_case_context
        }

# Example usage and testing
if __name__ == "__main__":
    # Test data validation
    test_profile = {
        'organization_name': 'Test Organization',
        'sector': 'government',
        'use_case_category': 'citizen_services',
        'target_user_base': 100000,
        'contact_email': 'test@example.com'
    }
    
    validator = DataValidator()
    validation_errors = validator.validate_customer_profile(test_profile)
    
    if validation_errors:
        print("Validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("Profile validation passed")
    
    # Test data transformation
    transformer = DataTransformer()
    
    # Create sample profile object
    sample_profile = CustomerProfile(
        tenant_id='test_tenant',
        organization_name='Test Organization',
        sector='government',
        use_case_category='citizen_services',
        specific_use_cases=['document_translation'],
        target_user_base=100000,
        geographical_coverage=['India'],
        languages_required=['English', 'Hindi'],
        business_goals=['Improve citizen services'],
        success_metrics=['Faster processing'],
        sla_tier='premium',
        contact_email='test@example.com'
    )
    
    # Transform to API response
    api_response = transformer.profile_to_api_response(sample_profile)
    print("\nAPI Response:")
    print(json.dumps(api_response, indent=2))
