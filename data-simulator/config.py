import os
# Removed dotenv loading to avoid conflicts with Docker environment variables


class Config:
    """Configuration class for the Bhashini QoS Data Simulator"""

    # InfluxDB Configuration
    INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://127.0.0.1:8086')
    INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'admin-token-123')  # Fallback token
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'bhashini')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'qos_metrics')

    # Simulation Configuration
    SIMULATION_INTERVAL = int(os.getenv('SIMULATION_INTERVAL', 10))  # seconds
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Service Configurations for Bhashini APIs
    SERVICES = {
        'translation': {
            'name': 'Translation Service',
            'latency': {
                'mean': 150,  # milliseconds
                'std': 30,
                'min': 80,
                'max': 300
            },
            'error_rate': {
                'base': 0.02,  # 2% base error rate
                'peak_multiplier': 3.0  # 3x during peak hours
            },
            'throughput': {
                'base': 100,  # requests per minute
                'peak_multiplier': 2.5
            }
        },
        'tts': {
            'name': 'Text-to-Speech Service',
            'latency': {
                'mean': 200,
                'std': 50,
                'min': 120,
                'max': 500
            },
            'error_rate': {
                'base': 0.015,
                'peak_multiplier': 2.5
            },
            'throughput': {
                'base': 80,
                'peak_multiplier': 2.0
            }
        },
        'asr': {
            'name': 'Automatic Speech Recognition',
            'latency': {
                'mean': 180,
                'std': 40,
                'min': 100,
                'max': 400
            },
            'error_rate': {
                'base': 0.025,
                'peak_multiplier': 3.5
            },
            'throughput': {
                'base': 90,
                'peak_multiplier': 2.2
            }
        }
    }

    # Customer Tenant Definitions
    TENANTS = {
        'enterprise_1': {
            'name': 'Enterprise Customer 1',
            'sla_tier': 'premium',
            'latency_multiplier': 0.8,  # 20% better than baseline
            'error_rate_multiplier': 0.5,  # 50% better than baseline
            'traffic_multiplier': 2.0  # 2x more traffic
        },
        'enterprise_2': {
            'name': 'Enterprise Customer 2',
            'sla_tier': 'premium',
            'latency_multiplier': 0.85,
            'error_rate_multiplier': 0.6,
            'traffic_multiplier': 1.8
        },
        'startup_1': {
            'name': 'Startup Customer 1',
            'sla_tier': 'standard',
            'latency_multiplier': 1.0,  # baseline performance
            'error_rate_multiplier': 1.0,
            'traffic_multiplier': 0.8
        },
        'startup_2': {
            'name': 'Startup Customer 2',
            'sla_tier': 'standard',
            'latency_multiplier': 1.1,
            'error_rate_multiplier': 1.2,
            'traffic_multiplier': 0.6
        },
        'freemium_1': {
            'name': 'Freemium Customer 1',
            'sla_tier': 'basic',
            'latency_multiplier': 1.3,
            'error_rate_multiplier': 1.5,
            'traffic_multiplier': 0.4
        }
    }

    # Time-based Traffic Patterns
    TRAFFIC_PATTERNS = {
        'business_hours': {
            'start': 9,  # 9 AM
            'end': 18,   # 6 PM
            'multiplier': 1.5
        },
        'peak_hours': {
            'start': 11,  # 11 AM
            'end': 14,    # 2 PM
            'multiplier': 2.0
        },
        'weekend_multiplier': 0.6,
        'maintenance_window': {
            'start': 2,   # 2 AM
            'end': 4,     # 4 AM
            'multiplier': 0.3
        }
    }

    # Metric Generation Parameters
    METRICS = {
        'batch_size': 100,  # metrics per batch write
        'retry_attempts': 3,
        'retry_delay': 1,   # seconds
        'correlation_factor': 0.7  # correlation between load and latency
    }
