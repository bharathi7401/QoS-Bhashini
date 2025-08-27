"""
REST API Server for Bhashini Business Intelligence System

This module provides a comprehensive FastAPI server including:
- Customer profile management endpoints
- Value estimation queries
- Recommendation retrieval
- Authentication and authorization middleware
- API documentation and OpenAPI specs
- Health checks and monitoring
- Rate limiting and error handling
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, Field
import uvicorn
from contextlib import asynccontextmanager

# Import business intelligence components
from .customer_profiler import CustomerProfiler
from .value_estimator import ValueEstimator, QoSMetrics
from .recommendation_engine import RecommendationEngine
from .data_models import (
    CustomerProfileCreate, CustomerProfileUpdate, ValueEstimateCreate,
    RecommendationCreate, DatabaseManager, DataValidator, DataTransformer
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# API configuration
API_TITLE = "Bhashini Business Intelligence API"
API_DESCRIPTION = "Comprehensive API for customer profiling, value estimation, and optimization recommendations"
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # requests per window

# Global variables for components
customer_profiler: Optional[CustomerProfiler] = None
value_estimator: Optional[ValueEstimator] = None
recommendation_engine: Optional[RecommendationEngine] = None
database_manager: Optional[DatabaseManager] = None

# Rate limiting storage
request_counts: Dict[str, List[datetime]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Bhashini Business Intelligence API...")
    
    try:
        # Initialize database manager
        global database_manager
        database_url = "postgresql://user:password@localhost/bhashini_bi"
        database_manager = DatabaseManager(database_url)
        logger.info("Database manager initialized")
        
        # Initialize customer profiler
        global customer_profiler
        customer_profiler = CustomerProfiler()
        logger.info("Customer profiler initialized")
        
        # Initialize value estimator
        global value_estimator
        value_estimator = ValueEstimator()
        logger.info("Value estimator initialized")
        
        # Initialize recommendation engine
        global recommendation_engine
        recommendation_engine = RecommendationEngine()
        logger.info("Recommendation engine initialized")
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bhashini Business Intelligence API...")
    if database_manager:
        database_manager.engine.dispose()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate authentication token and return user ID"""
    # This is a simplified authentication - implement proper JWT validation in production
    token = credentials.credentials
    
    # For demo purposes, accept any token
    # In production, validate JWT tokens against your authentication service
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # Extract user/tenant ID from token (simplified)
    # In production, decode JWT and extract user information
    user_id = f"user_{token[:8]}"  # Simplified user ID extraction
    
    return user_id

async def rate_limit_check(request: Request):
    """Check rate limiting for the request"""
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old requests outside the window
    if client_ip in request_counts:
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if current_time - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
        ]
    
    # Check if client has exceeded rate limit
    if client_ip in request_counts and len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Add current request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)

# Response models
class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check component health
        components_healthy = all([
            customer_profiler is not None,
            value_estimator is not None,
            recommendation_engine is not None,
            database_manager is not None
        ])
        
        if components_healthy:
            return APIResponse(
                success=True,
                message="All components healthy",
                data={
                    "status": "healthy",
                    "components": {
                        "customer_profiler": "healthy",
                        "value_estimator": "healthy",
                        "recommendation_engine": "healthy",
                        "database_manager": "healthy"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            return APIResponse(
                success=False,
                message="Some components unhealthy",
                data={
                    "status": "unhealthy",
                    "components": {
                        "customer_profiler": "healthy" if customer_profiler else "unhealthy",
                        "value_estimator": "healthy" if value_estimator else "unhealthy",
                        "recommendation_engine": "healthy" if recommendation_engine else "unhealthy",
                        "database_manager": "healthy" if database_manager else "unhealthy"
                    }
                }
            )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return APIResponse(
            success=False,
            message="Health check failed",
            data={"error": str(e)}
        )

# Customer Profile Management Endpoints
@app.post(f"{API_PREFIX}/profiles", tags=["Customer Profiles"], response_model=APIResponse)
async def create_customer_profile(
    profile_data: CustomerProfileCreate,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Create a new customer profile"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        # Validate profile data
        validator = DataValidator()
        validation_errors = validator.validate_customer_profile(profile_data.dict())
        
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation errors: {', '.join(validation_errors)}"
            )
        
        # Create profile
        profile = customer_profiler.create_profile_from_form(profile_data.dict())
        
        # Transform to API response
        transformer = DataTransformer()
        profile_response = transformer.profile_to_api_response(profile)
        
        logger.info(f"Created customer profile for {profile.organization_name}")
        
        return APIResponse(
            success=True,
            message="Customer profile created successfully",
            data=profile_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get(f"{API_PREFIX}/profiles", tags=["Customer Profiles"], response_model=APIResponse)
async def list_customer_profiles(
    sector: Optional[str] = None,
    use_case: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """List customer profiles with optional filtering"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        profiles = []
        
        if sector:
            profiles = customer_profiler.get_profiles_by_sector(sector)
        elif use_case:
            profiles = customer_profiler.get_profiles_by_use_case(use_case)
        else:
            # Get all profiles
            profiles = list(customer_profiler.profiles.values())
        
        # Apply status filter if specified
        if status_filter:
            profiles = [p for p in profiles if p.profile_status == status_filter]
        
        # Transform to API responses
        transformer = DataTransformer()
        profile_responses = [transformer.profile_to_api_response(p) for p in profiles]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(profile_responses)} customer profiles",
            data={
                "profiles": profile_responses,
                "total_count": len(profile_responses),
                "filters_applied": {
                    "sector": sector,
                    "use_case": use_case,
                    "status": status_filter
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing customer profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get(f"{API_PREFIX}/profiles/{{tenant_id}}", tags=["Customer Profiles"], response_model=APIResponse)
async def get_customer_profile(
    tenant_id: str,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Get a specific customer profile by tenant ID"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        profile = customer_profiler.get_profile(tenant_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # Transform to API response
        transformer = DataTransformer()
        profile_response = transformer.profile_to_api_response(profile)
        
        return APIResponse(
            success=True,
            message="Customer profile retrieved successfully",
            data=profile_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.put(f"{API_PREFIX}/profiles/{{tenant_id}}", tags=["Customer Profiles"], response_model=APIResponse)
async def update_customer_profile(
    tenant_id: str,
    profile_updates: CustomerProfileUpdate,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Update an existing customer profile"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        # Get current profile
        current_profile = customer_profiler.get_profile(tenant_id)
        if not current_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # Update profile
        updated_profile = customer_profiler.update_profile(tenant_id, profile_updates.dict(exclude_unset=True))
        
        # Transform to API response
        transformer = DataTransformer()
        profile_response = transformer.profile_to_api_response(updated_profile)
        
        logger.info(f"Updated customer profile for {updated_profile.organization_name}")
        
        return APIResponse(
            success=True,
            message="Customer profile updated successfully",
            data=profile_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete(f"{API_PREFIX}/profiles/{{tenant_id}}", tags=["Customer Profiles"], response_model=APIResponse)
async def deactivate_customer_profile(
    tenant_id: str,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Deactivate a customer profile"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        success = customer_profiler.deactivate_profile(tenant_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        logger.info(f"Deactivated customer profile for tenant: {tenant_id}")
        
        return APIResponse(
            success=True,
            message="Customer profile deactivated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Value Estimation Endpoints
@app.post(f"{API_PREFIX}/value-estimation", tags=["Value Estimation"], response_model=APIResponse)
async def calculate_customer_value(
    tenant_id: str,
    qos_metrics: List[Dict[str, Any]],
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Calculate business value for a customer based on QoS metrics"""
    try:
        if not value_estimator or not customer_profiler:
            raise HTTPException(status_code=500, detail="Value estimator not initialized")
        
        # Get customer profile
        profile = customer_profiler.get_profile(tenant_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # Convert QoS metrics to proper format
        qos_objects = []
        for metric in qos_metrics:
            qos_obj = QoSMetrics(
                tenant_id=tenant_id,
                timestamp=datetime.now(),
                service_type=metric.get('service_type', 'unknown'),
                latency_ms=metric.get('latency_ms', 0),
                throughput_rps=metric.get('throughput_rps', 0),
                error_rate=metric.get('error_rate', 0),
                availability_percent=metric.get('availability_percent', 100),
                response_time_p95=metric.get('response_time_p95', 0)
            )
            qos_objects.append(qos_obj)
        
        # Calculate value
        value_metrics = value_estimator.calculate_customer_value(profile.__dict__, qos_objects)
        
        # Generate value report
        value_report = value_estimator.generate_value_report(value_metrics, profile.__dict__)
        
        logger.info(f"Calculated value for tenant {tenant_id}: {value_metrics.total_value_score:.1f}/100")
        
        return APIResponse(
            success=True,
            message="Value estimation completed successfully",
            data={
                "value_metrics": value_metrics.__dict__,
                "value_report": value_report
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating customer value: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get(f"{API_PREFIX}/value-estimation/{{tenant_id}}", tags=["Value Estimation"], response_model=APIResponse)
async def get_value_estimation(
    tenant_id: str,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Get value estimation for a specific customer"""
    try:
        if not value_estimator or not customer_profiler:
            raise HTTPException(status_code=500, detail="Value estimator not initialized")
        
        # Get customer profile
        profile = customer_profiler.get_profile(tenant_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # For demo purposes, generate sample QoS metrics
        # In production, this would query actual QoS data from InfluxDB
        sample_qos_metrics = [
            QoSMetrics(
                tenant_id=tenant_id,
                timestamp=datetime.now(),
                service_type='translation',
                latency_ms=1500,
                throughput_rps=200,
                error_rate=0.02,
                availability_percent=99.5,
                response_time_p95=2500
            ),
            QoSMetrics(
                tenant_id=tenant_id,
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
        value_metrics = value_estimator.calculate_customer_value(profile.__dict__, sample_qos_metrics)
        
        # Generate value report
        value_report = value_estimator.generate_value_report(value_metrics, profile.__dict__)
        
        return APIResponse(
            success=True,
            message="Value estimation retrieved successfully",
            data={
                "value_metrics": value_metrics.__dict__,
                "value_report": value_report
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving value estimation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Recommendation Endpoints
@app.post(f"{API_PREFIX}/recommendations", tags=["Recommendations"], response_model=APIResponse)
async def generate_recommendations(
    tenant_id: str,
    qos_metrics: List[Dict[str, Any]],
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Generate optimization recommendations for a customer"""
    try:
        if not recommendation_engine or not customer_profiler:
            raise HTTPException(status_code=500, detail="Recommendation engine not initialized")
        
        # Get customer profile
        profile = customer_profiler.get_profile(tenant_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # Analyze QoS metrics
        qos_analysis = recommendation_engine.analyze_qos_metrics(tenant_id, qos_metrics)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(qos_analysis, profile.__dict__)
        
        # Generate recommendation report
        recommendation_report = recommendation_engine.generate_recommendation_report(
            recommendations, qos_analysis, profile.__dict__
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations for tenant {tenant_id}")
        
        return APIResponse(
            success=True,
            message="Recommendations generated successfully",
            data={
                "qos_analysis": qos_analysis.__dict__,
                "recommendations": [r.__dict__ for r in recommendations],
                "recommendation_report": recommendation_report
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get(f"{API_PREFIX}/recommendations/{{tenant_id}}", tags=["Recommendations"], response_model=APIResponse)
async def get_recommendations(
    tenant_id: str,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Get recommendations for a specific customer"""
    try:
        if not recommendation_engine or not customer_profiler:
            raise HTTPException(status_code=500, detail="Recommendation engine not initialized")
        
        # Get customer profile
        profile = customer_profiler.get_profile(tenant_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer profile not found for tenant: {tenant_id}"
            )
        
        # For demo purposes, generate sample QoS metrics
        # In production, this would query actual QoS data from InfluxDB
        sample_qos_metrics = [
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
        
        # Analyze QoS metrics
        qos_analysis = recommendation_engine.analyze_qos_metrics(tenant_id, sample_qos_metrics)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(qos_analysis, profile.__dict__)
        
        # Generate recommendation report
        recommendation_report = recommendation_engine.generate_recommendation_report(
            recommendations, qos_analysis, profile.__dict__
        )
        
        return APIResponse(
            success=True,
            message="Recommendations retrieved successfully",
            data={
                "qos_analysis": qos_analysis.__dict__,
                "recommendations": [r.__dict__ for r in recommendations],
                "recommendation_report": recommendation_report
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Analytics and Reporting Endpoints
@app.get(f"{API_PREFIX}/analytics/summary", tags=["Analytics"], response_model=APIResponse)
async def get_analytics_summary(
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Get analytics summary for all customers"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        # Get profile statistics
        profile_stats = customer_profiler.get_profile_statistics()
        
        return APIResponse(
            success=True,
            message="Analytics summary retrieved successfully",
            data=profile_stats
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get(f"{API_PREFIX}/analytics/sector/{{sector}}", tags=["Analytics"], response_model=APIResponse)
async def get_sector_analytics(
    sector: str,
    current_user: str = Depends(get_current_user),
    request: Request = Depends(rate_limit_check)
):
    """Get analytics for a specific sector"""
    try:
        if not customer_profiler:
            raise HTTPException(status_code=500, detail="Customer profiler not initialized")
        
        # Get profiles for the sector
        sector_profiles = customer_profiler.get_profiles_by_sector(sector)
        
        # Calculate sector-specific metrics
        sector_metrics = {
            "sector": sector,
            "total_customers": len(sector_profiles),
            "sla_distribution": {},
            "use_case_distribution": {},
            "average_user_base": 0
        }
        
        if sector_profiles:
            sla_counts = {}
            use_case_counts = {}
            total_users = 0
            
            for profile in sector_profiles:
                # SLA distribution
                sla_tier = profile.sla_tier
                sla_counts[sla_tier] = sla_counts.get(sla_tier, 0) + 1
                
                # Use case distribution
                use_case = profile.use_case_category
                use_case_counts[use_case] = use_case_counts.get(use_case, 0) + 1
                
                # Total users
                total_users += profile.target_user_base
            
            sector_metrics["sla_distribution"] = sla_counts
            sector_metrics["use_case_distribution"] = use_case_counts
            sector_metrics["average_user_base"] = total_users // len(sector_profiles)
        
        return APIResponse(
            success=True,
            message=f"Sector analytics retrieved successfully for {sector}",
            data=sector_metrics
        )
        
    except Exception as e:
        logger.error(f"Error retrieving sector analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            message=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Main entry point
if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
