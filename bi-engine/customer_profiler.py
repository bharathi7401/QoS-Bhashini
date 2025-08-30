"""
Customer Profiling System for Bhashini QoS Monitoring

This module provides comprehensive customer profiling capabilities including:
- Application form data processing and validation
- Customer profile management with sector classification
- Integration with existing tenant configuration system
- Profile update mechanisms and historical tracking
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CustomerProfile:
    """Data model for customer profile information"""
    tenant_id: str
    organization_name: str
    sector: str  # government, private, NGO
    use_case_category: str  # citizen_services, healthcare, education, etc.
    specific_use_cases: List[str]
    target_user_base: int
    geographical_coverage: List[str]
    languages_required: List[str]
    business_goals: List[str]
    success_metrics: List[str]
    sla_tier: str  # premium, standard, basic
    profile_created_date: datetime
    last_updated: datetime
    profile_status: str  # active, inactive, pending
    contact_email: str
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None

class CustomerProfiler:
    """Main customer profiling system"""
    
    def __init__(self, tenant_config_path: str = "config/tenant-config.yml"):
        self.tenant_config_path = Path(tenant_config_path)
        self.profiles: Dict[str, CustomerProfile] = {}
        self._load_existing_tenants()
    
    def _load_existing_tenants(self):
        """Load existing tenant configurations and create initial profiles"""
        try:
            if self.tenant_config_path.exists():
                with open(self.tenant_config_path, 'r') as f:
                    tenant_config = yaml.safe_load(f)
                
                # Create profiles for existing tenants
                for tenant in tenant_config.get('tenants', []):
                    profile = self._create_profile_from_tenant(tenant)
                    if profile:
                        self.profiles[profile.tenant_id] = profile
                        logger.info(f"Created profile for existing tenant: {profile.organization_name}")
        except Exception as e:
            logger.error(f"Error loading existing tenants: {e}")
    
    def _create_profile_from_tenant(self, tenant: Dict) -> Optional[CustomerProfile]:
        """Create a customer profile from existing tenant configuration"""
        try:
            # Infer sector and use case from organization name and SLA tier
            org_name = tenant.get('name', 'Unknown')
            sla_tier = tenant.get('sla_tier', 'basic')
            
            # Simple inference logic - can be enhanced with ML
            sector = self._infer_sector_from_name(org_name)
            use_case = self._infer_use_case_from_sector(sector)
            
            return CustomerProfile(
                tenant_id=tenant.get('id', 'unknown'),
                organization_name=org_name,
                sector=sector,
                use_case_category=use_case,
                specific_use_cases=[use_case],
                target_user_base=self._estimate_user_base(sla_tier),
                geographical_coverage=['India'],  # Default assumption
                languages_required=['English', 'Hindi'],  # Default assumption
                business_goals=['Improve service accessibility', 'Reduce operational costs'],
                success_metrics=['User satisfaction', 'Service efficiency'],
                sla_tier=sla_tier,
                profile_created_date=datetime.now(),
                last_updated=datetime.now(),
                profile_status='active',
                contact_email=f"admin@{org_name.lower().replace(' ', '')}.com"
            )
        except Exception as e:
            logger.error(f"Error creating profile from tenant {tenant}: {e}")
            return None
    
    def _infer_sector_from_name(self, org_name: str) -> str:
        """Infer sector from organization name"""
        org_lower = org_name.lower()
        
        # Government indicators
        if any(word in org_lower for word in ['ministry', 'department', 'government', 'govt', 'public']):
            return 'government'
        
        # Healthcare indicators
        if any(word in org_lower for word in ['hospital', 'medical', 'health', 'clinic', 'pharma']):
            return 'healthcare'
        
        # Education indicators
        if any(word in org_lower for word in ['university', 'college', 'school', 'education', 'academy']):
            return 'education'
        
        # NGO indicators
        if any(word in org_lower for word in ['foundation', 'trust', 'ngo', 'charity', 'social']):
            return 'NGO'
        
        # Default to private sector
            return 'private'
    
    def _infer_use_case_from_sector(self, sector: str) -> str:
        """Infer use case category from sector"""
        sector_use_cases = {
            'government': 'citizen_services',
            'healthcare': 'patient_communication',
            'education': 'content_localization',
            'NGO': 'community_services',
            'private': 'business_operations'
        }
        return sector_use_cases.get(sector, 'general')
    
    def _estimate_user_base(self, sla_tier: str) -> int:
        """Estimate user base based on SLA tier"""
        tier_estimates = {
            'premium': 1000000,  # 1M users
            'standard': 100000,   # 100K users
            'basic': 10000        # 10K users
        }
        return tier_estimates.get(sla_tier, 10000)
    
    def create_profile_from_form(self, form_data: Dict[str, Any]) -> CustomerProfile:
        """Create a new customer profile from application form data"""
        try:
            # Validate required fields
            required_fields = ['organization_name', 'sector', 'use_case_category', 'target_user_base']
            for field in required_fields:
                if field not in form_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create profile
            profile = CustomerProfile(
                tenant_id=form_data.get('tenant_id', self._generate_tenant_id()),
                organization_name=form_data['organization_name'],
                sector=form_data['sector'],
                use_case_category=form_data['use_case_category'],
                specific_use_cases=form_data.get('specific_use_cases', []),
                target_user_base=form_data['target_user_base'],
                geographical_coverage=form_data.get('geographical_coverage', ['India']),
                languages_required=form_data.get('languages_required', ['English']),
                business_goals=form_data.get('business_goals', []),
                success_metrics=form_data.get('success_metrics', []),
                sla_tier=form_data.get('sla_tier', 'basic'),
                profile_created_date=datetime.now(),
                last_updated=datetime.now(),
                profile_status='pending',
                contact_email=form_data.get('contact_email', ''),
                contact_phone=form_data.get('contact_phone'),
                industry=form_data.get('industry'),
                annual_revenue=form_data.get('annual_revenue'),
                employee_count=form_data.get('employee_count')
            )
            
            # Validate profile
            self._validate_profile(profile)
            
            # Store profile
            self.profiles[profile.tenant_id] = profile
            logger.info(f"Created new profile for {profile.organization_name}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile from form data: {e}")
            raise
    
    def _generate_tenant_id(self) -> str:
        """Generate a unique tenant ID"""
        import uuid
        return f"tenant_{uuid.uuid4().hex[:8]}"
    
    def _validate_profile(self, profile: CustomerProfile):
        """Validate profile completeness and consistency"""
        # Validate sector
        valid_sectors = ['government', 'private', 'NGO', 'healthcare', 'education']
        if profile.sector not in valid_sectors:
            raise ValueError(f"Invalid sector: {profile.sector}")
        
        # Validate use case category
        valid_use_cases = [
            'citizen_services', 'healthcare', 'education', 'business_operations',
            'community_services', 'content_localization', 'patient_communication'
        ]
        if profile.use_case_category not in valid_use_cases:
            raise ValueError(f"Invalid use case category: {profile.use_case_category}")
        
        # Validate target user base
        if profile.target_user_base <= 0:
            raise ValueError("Target user base must be positive")
        
        # Validate contact email
        if not profile.contact_email or '@' not in profile.contact_email:
            raise ValueError("Invalid contact email")
    
    def update_profile(self, tenant_id: str, updates: Dict[str, Any]) -> CustomerProfile:
        """Update an existing customer profile"""
        if tenant_id not in self.profiles:
            raise ValueError(f"Profile not found for tenant: {tenant_id}")
        
        profile = self.profiles[tenant_id]
        
        # Update fields
        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        # Update timestamp
        profile.last_updated = datetime.now()
        
        # Validate updated profile
        self._validate_profile(profile)
        
        logger.info(f"Updated profile for {profile.organization_name}")
        return profile
    
    def get_profile(self, tenant_id: str) -> Optional[CustomerProfile]:
        """Retrieve a customer profile by tenant ID"""
        return self.profiles.get(tenant_id)
    
    def get_profiles_by_sector(self, sector: str) -> List[CustomerProfile]:
        """Get all profiles for a specific sector"""
        return [profile for profile in self.profiles.values() if profile.sector == sector]
    
    def get_profiles_by_use_case(self, use_case: str) -> List[CustomerProfile]:
        """Get all profiles for a specific use case"""
        return [profile for profile in self.profiles.values() if profile.use_case_category == use_case]
    
    def search_profiles(self, query: str) -> List[CustomerProfile]:
        """Search profiles by organization name or description"""
        query_lower = query.lower()
        results = []
        
        for profile in self.profiles.values():
            if (query_lower in profile.organization_name.lower() or
                query_lower in profile.sector.lower() or
                query_lower in profile.use_case_category.lower()):
                results.append(profile)
        
        return results
    
    def deactivate_profile(self, tenant_id: str) -> bool:
        """Deactivate a customer profile"""
        if tenant_id in self.profiles:
            self.profiles[tenant_id].profile_status = 'inactive'
            self.profiles[tenant_id].last_updated = datetime.now()
            logger.info(f"Deactivated profile for tenant: {tenant_id}")
            return True
        return False
    
    def export_profiles(self, format: str = 'json') -> str:
        """Export all profiles in specified format"""
        if format == 'json':
            profiles_data = [asdict(profile) for profile in self.profiles.values()]
            # Convert datetime objects to strings for JSON serialization
            for profile_data in profiles_data:
                profile_data['profile_created_date'] = profile_data['profile_created_date'].isoformat()
                profile_data['last_updated'] = profile_data['last_updated'].isoformat()
            return json.dumps(profiles_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get statistics about customer profiles"""
        total_profiles = len(self.profiles)
        sector_counts = {}
        use_case_counts = {}
        sla_tier_counts = {}
        
        for profile in self.profiles.values():
            sector_counts[profile.sector] = sector_counts.get(profile.sector, 0) + 1
            use_case_counts[profile.use_case_category] = use_case_counts.get(profile.use_case_category, 0) + 1
            sla_tier_counts[profile.sla_tier] = sla_tier_counts.get(profile.sla_tier, 0) + 1
        
        return {
            'total_profiles': total_profiles,
            'sector_distribution': sector_counts,
            'use_case_distribution': use_case_counts,
            'sla_tier_distribution': sla_tier_counts,
            'active_profiles': len([p for p in self.profiles.values() if p.profile_status == 'active']),
            'pending_profiles': len([p for p in self.profiles.values() if p.profile_status == 'pending'])
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize profiler
    profiler = CustomerProfiler()
    
    # Print statistics
    stats = profiler.get_profile_statistics()
    print("Profile Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example form data
    form_data = {
        'organization_name': 'Ministry of Digital India',
        'sector': 'government',
        'use_case_category': 'citizen_services',
        'target_user_base': 5000000,
        'specific_use_cases': ['document_translation', 'citizen_portal'],
        'geographical_coverage': ['India'],
        'languages_required': ['English', 'Hindi', 'Tamil', 'Telugu'],
        'business_goals': ['Digital India initiative', 'Citizen service accessibility'],
        'success_metrics': ['Citizen satisfaction', 'Service efficiency'],
        'contact_email': 'admin@digitalindia.gov.in'
    }
    
    # Create profile
    try:
        profile = profiler.create_profile_from_form(form_data)
        print(f"\nCreated profile for: {profile.organization_name}")
        print(f"Sector: {profile.sector}")
        print(f"Use Case: {profile.use_case_category}")
        print(f"Target Users: {profile.target_user_base:,}")
    except Exception as e:
        print(f"Error creating profile: {e}")
