import time
import logging
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from config import Config


class InfluxDBClientWrapper:
    """InfluxDB client wrapper for writing time-series QoS metrics"""

    def __init__(self):
        self.config = Config()
        self.client = None
        self.write_api = None
        self.query_api = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish connection to InfluxDB"""
        try:
            self.client = InfluxDBClient(
                url=self.config.INFLUXDB_URL,
                token=self.config.INFLUXDB_TOKEN,
                org=self.config.INFLUXDB_ORG,
                timeout=30_000
            )

            # Test connection
            self.client.ping()

            # Test token permissions with a quick query
            try:
                self.query_api = self.client.query_api()
                self.query_api.query(f'from(bucket: "{self.config.INFLUXDB_BUCKET}") |> range(start: -1m) |> limit(n:1)', org=self.config.INFLUXDB_ORG)
            except Exception:
                self.logger.error("Token lacks permission or is invalid")
                return False

            # Initialize APIs
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

            self.logger.info(f"Successfully connected to InfluxDB at {self.config.INFLUXDB_URL}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to InfluxDB: {str(e)}")
            return False

    def disconnect(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from InfluxDB")

    def write_metrics_batch(self, metrics_batch):
        """Write a batch of metrics to InfluxDB with retry logic"""
        if not self.client or not self.write_api:
            self.logger.error("InfluxDB client not connected")
            return False

        for attempt in range(self.config.METRICS['retry_attempts']):
            try:
                # Convert metrics to InfluxDB Point objects
                points = []
                for metric in metrics_batch:
                    point = Point(metric['measurement'])

                    # Add tags
                    for tag_key, tag_value in metric['tags'].items():
                        point.tag(tag_key, str(tag_value))

                    # Add fields
                    for field_key, field_value in metric['fields'].items():
                        point.field(field_key, field_value)

                    # Add timestamp
                    if isinstance(metric['time'], datetime):
                        point.time(metric['time'], WritePrecision.NS)
                    else:
                        point.time(metric['time'], WritePrecision.NS)

                    points.append(point)

                # Write batch
                self.write_api.write(
                    bucket=self.config.INFLUXDB_BUCKET,
                    org=self.config.INFLUXDB_ORG,
                    record=points
                )

                self.logger.info(f"Successfully wrote {len(points)} metrics to InfluxDB")
                return True

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.config.METRICS['retry_attempts'] - 1:
                    time.sleep(self.config.METRICS['retry_delay'])
                else:
                    self.logger.error("All retry attempts failed for metrics batch")
                    return False

        return False

    def write_single_metric(self, measurement, tags, fields, timestamp=None):
        """Write a single metric to InfluxDB"""
        if not self.client or not self.write_api:
            self.logger.error("InfluxDB client not connected")
            return False

        try:
            point = Point(measurement)

            # Add tags
            for tag_key, tag_value in tags.items():
                point.tag(tag_key, str(tag_value))

            # Add fields
            for field_key, field_value in fields.items():
                point.field(field_key, field_value)

            # Add timestamp
            if timestamp:
                point.time(timestamp, WritePrecision.NS)

            # Write point
            self.write_api.write(
                bucket=self.config.INFLUXDB_BUCKET,
                org=self.config.INFLUXDB_ORG,
                record=point
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to write single metric: {str(e)}")
            return False

    def query_metrics(self, query, params=None):
        """Execute a Flux query against InfluxDB"""
        if not self.client or not self.query_api:
            self.logger.error("InfluxDB client not connected")
            return None

        try:
            if params:
                # Replace parameters in query
                for key, value in params.items():
                    query = query.replace(f"${key}", str(value))

            result = self.query_api.query(query, org=self.config.INFLUXDB_ORG)
            return result

        except Exception as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            return None

    def get_recent_metrics(self, minutes=10, tenant_id=None, service_name=None):
        """Get recent metrics with optional filtering"""
        query = f'''
        from(bucket: "{self.config.INFLUXDB_BUCKET}")
            |> range(start: -{minutes}m)
            |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
        '''

        if tenant_id:
            query += f'|> filter(fn: (r) => r["tenant_id"] == "{tenant_id}")\n'

        if service_name:
            query += f'|> filter(fn: (r) => r["service_name"] == "{service_name}")\n'

        query += '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\n'

        return self.query_metrics(query)

    def get_metrics_summary(self, hours=24):
        """Get metrics summary for the last N hours"""
        query = f'''
        from(bucket: "{self.config.INFLUXDB_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
            |> group(columns: ["metric_type", "tenant_id", "service_name"])
            |> mean()
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''

        return self.query_metrics(query)

    def is_healthy(self):
        """Check if InfluxDB connection is healthy"""
        try:
            if self.client:
                self.client.ping()
                return True
            return False
        except Exception:
            return False
