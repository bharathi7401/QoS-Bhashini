import random
from datetime import datetime
import numpy as np
from config import Config


class MetricsGenerator:
    """Generates realistic QoS metrics for Bhashini services"""

    def __init__(self):
        self.config = Config()
        self.current_time = datetime.now()

    def get_time_multiplier(self):
        """Calculate time-based traffic multiplier"""
        hour = self.current_time.hour
        is_weekend = self.current_time.weekday() >= 5

        # Business hours multiplier
        if self.config.TRAFFIC_PATTERNS['business_hours']['start'] <= hour <= self.config.TRAFFIC_PATTERNS['business_hours']['end']:
            multiplier = self.config.TRAFFIC_PATTERNS['business_hours']['multiplier']
        else:
            multiplier = 1.0

        # Peak hours multiplier
        if self.config.TRAFFIC_PATTERNS['peak_hours']['start'] <= hour <= self.config.TRAFFIC_PATTERNS['peak_hours']['end']:
            multiplier *= self.config.TRAFFIC_PATTERNS['peak_hours']['multiplier']

        # Weekend multiplier
        if is_weekend:
            multiplier *= self.config.TRAFFIC_PATTERNS['weekend_multiplier']

        # Maintenance window multiplier
        if self.config.TRAFFIC_PATTERNS['maintenance_window']['start'] <= hour <= self.config.TRAFFIC_PATTERNS['maintenance_window']['end']:
            multiplier *= self.config.TRAFFIC_PATTERNS['maintenance_window']['multiplier']

        return max(0.1, multiplier)  # Ensure minimum traffic

    def generate_latency(self, service_name, tenant_id):
        """Generate realistic API latency using Gaussian distribution"""
        service_config = self.config.SERVICES[service_name]
        tenant_config = self.config.TENANTS[tenant_id]

        # Base latency with Gaussian distribution
        base_latency = np.random.normal(
            service_config['latency']['mean'],
            service_config['latency']['std']
        )

        # Apply tenant-specific multiplier
        latency = base_latency * tenant_config['latency_multiplier']

        # Apply time-based variations
        time_multiplier = self.get_time_multiplier()
        latency *= (1 + (time_multiplier - 1) * 0.3)  # 30% impact from traffic

        # Ensure within bounds
        latency = max(service_config['latency']['min'],
                      min(service_config['latency']['max'], latency))

        return float(round(latency, 2))

    def generate_error_rate(self, service_name, tenant_id):
        """Generate realistic error rates using probability distributions"""
        service_config = self.config.SERVICES[service_name]
        tenant_config = self.config.TENANTS[tenant_id]

        # Base error rate
        base_error_rate = service_config['error_rate']['base']

        # Apply tenant-specific multiplier
        error_rate = base_error_rate * tenant_config['error_rate_multiplier']

        # Add time-based variations (higher errors during peak hours)
        time_multiplier = self.get_time_multiplier()
        if time_multiplier > 1.5:  # During peak hours
            error_rate *= service_config['error_rate']['peak_multiplier']

        # Add some randomness
        error_rate *= random.uniform(0.8, 1.2)

        # Ensure reasonable bounds
        error_rate = max(0.001, min(0.15, error_rate))

        return float(round(error_rate, 4))

    def generate_throughput(self, service_name, tenant_id):
        """Generate realistic throughput using Poisson distribution"""
        service_config = self.config.SERVICES[service_name]
        tenant_config = self.config.TENANTS[tenant_id]

        # Base throughput
        base_throughput = service_config['throughput']['base']

        # Apply tenant-specific multiplier
        throughput = base_throughput * tenant_config['traffic_multiplier']

        # Apply time-based multiplier
        time_multiplier = self.get_time_multiplier()
        throughput *= time_multiplier

        # Add Poisson variation for realistic traffic patterns
        throughput = np.random.poisson(throughput)

        # Ensure minimum throughput
        throughput = max(1, throughput)

        return float(throughput)

    def generate_availability(self, service_name, tenant_id):
        """Generate service availability percentage"""
        base_availability = 99.5  # Base 99.5% availability

        # Premium tenants get better availability
        tenant_config = self.config.TENANTS[tenant_id]
        if tenant_config['sla_tier'] == 'premium':
            base_availability = 99.9
        elif tenant_config['sla_tier'] == 'basic':
            base_availability = 99.0

        # Add small variations
        availability = base_availability + random.uniform(-0.1, 0.1)

        return float(round(availability, 2))

    def generate_data_processed(self, service_name, tenant_id):
        """Generate data processed per request."""
        service_config = self.config.SERVICES[service_name]
        tenant_config = self.config.TENANTS[tenant_id]

        # Gaussian variation for realistic per-request values
        mean = service_config['data_processed']['mean']
        std = service_config['data_processed']['std']
        per_request = max(1, np.random.normal(mean, std))

        # Apply tenant traffic multiplier
        per_request *= tenant_config['traffic_multiplier']

        return float(round(per_request, 2)), service_config['data_processed']['unit']

    def generate_concurrent_users(self, service_name, tenant_id):
        """Simulate concurrent users supported."""
        tenant_config = self.config.TENANTS[tenant_id]

        base_users = 50  # baseline
        # Premium tenants handle more concurrent users
        if tenant_config['sla_tier'] == 'premium':
            base_users = 200
        elif tenant_config['sla_tier'] == 'standard':
            base_users = 100
        elif tenant_config['sla_tier'] == 'basic':
            base_users = 50

        # Add variability
        users = np.random.normal(base_users, base_users * 0.1)

        return max(1, int(users))

    def generate_regional_coverage(self, service_name):
        return self.config.REGIONAL_COVERAGE.get(service_name, 0)

    def generate_user_satisfaction(self, service_name, tenant_id):
        """Generate a satisfaction index (0–100)."""
        tenant_config = self.config.TENANTS[tenant_id]

        base_score = 80  # baseline satisfaction
        if tenant_config['sla_tier'] == 'premium':
            base_score = 90
        elif tenant_config['sla_tier'] == 'basic':
            base_score = 70

        # Add randomness
        score = np.random.normal(base_score, 5)

        # Clamp
        return float(round(min(100, max(50, score)), 2))


    def generate_metrics_batch(self):
        """Generate a complete batch of metrics for all services and tenants"""
        metrics = []
        self.current_time = datetime.now()

        for service_name in self.config.SERVICES.keys():
            for tenant_id in self.config.TENANTS.keys():
                # Generate metrics
                latency = self.generate_latency(service_name, tenant_id)
                error_rate = self.generate_error_rate(service_name, tenant_id)
                throughput = self.generate_throughput(service_name, tenant_id)
                availability = self.generate_availability(service_name, tenant_id)
                data_processed, unit = self.generate_data_processed(service_name, tenant_id)

                # Create metric points for each metric type
                service_tag = service_name.lower()
                metrics.extend([
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'latency',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': latency,
                            'unit': 'ms'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'error_rate',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': error_rate,
                            'unit': 'percent'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'throughput',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': throughput,
                            'unit': 'requests_per_minute'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'availability',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': availability,
                            'unit': 'percent'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'data_processed',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': data_processed,
                            'unit': unit
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'concurrent_users',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': self.generate_concurrent_users(service_name, tenant_id),
                            'unit': 'users'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'regional_coverage',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': self.generate_regional_coverage(service_name),
                            'unit': 'languages'
                        },
                        'time': self.current_time
                    },
                    {
                        'measurement': 'qos_metrics',
                        'tags': {
                            'customer_id': tenant_id,
                            'service': service_tag,
                            'metric_type': 'user_satisfaction',
                            'sla_tier': self.config.TENANTS[tenant_id]['sla_tier']
                        },
                        'fields': {
                            'value': self.generate_user_satisfaction(service_name, tenant_id),
                            'unit': 'percent'
                        },
                        'time': self.current_time
                    }

                ])

        return metrics

    def get_metrics_summary(self):
        """Get a summary of current metrics generation"""
        return {
            'services_count': len(self.config.SERVICES),
            'tenants_count': len(self.config.TENANTS),
            'metrics_per_batch': len(self.config.SERVICES) * len(self.config.TENANTS) * 8,
            'current_time': self.current_time.isoformat(),
            'time_multiplier': self.get_time_multiplier()
        }
