#!/usr/bin/env python3
"""
Bhashini QoS Data Simulator
Generates realistic QoS metrics for Bhashini Translation, TTS, and ASR services
"""

import sys
import time
import signal
import logging
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify
from metrics_generator import MetricsGenerator
from influx_client import InfluxDBClientWrapper
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config().LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BhashiniQoSSimulator:
    """Main simulator class for generating Bhashini QoS metrics"""

    def __init__(self):
        self.config = Config()
        self.metrics_generator = MetricsGenerator()
        self.influx_client = InfluxDBClientWrapper()
        self.running = False
        self.metrics_count = 0
        self.start_time = datetime.now()
        self.last_generation = None
        self.flask_started = False

        # Setup Flask app for health checks
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for health checks and monitoring"""
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            try:
                influxdb_connected = self.influx_client.is_healthy() if hasattr(self, 'influx_client') else False
            except Exception as e:
                logger.warning(f"Error checking InfluxDB health: {e}")
                influxdb_connected = False

            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'bhashini-qos-simulator',
                'version': '1.0.0',
                'liveness': 'ok',  # Process is running
                'readiness': 'ready' if influxdb_connected else 'not_ready',  # DB connection status
                'influxdb_connected': influxdb_connected,
                'metrics_generated': self.metrics_count,
                'last_generation': self.last_generation,
                'simulation_running': self.running,
                'flask_started': self.flask_started
            })

        @self.app.route('/status')
        def status():
            return jsonify({
                'running': self.running,
                'start_time': self.start_time.isoformat(),
                'metrics_generated': self.metrics_count,
                'last_generation': getattr(self, 'last_generation', 'Never'),
                'config': {
                    'simulation_interval': self.config.SIMULATION_INTERVAL,
                    'services_count': len(self.config.SERVICES),
                    'tenants_count': len(self.config.TENANTS)
                }
            })

        @self.app.route('/')
        def root():
            return jsonify({
                'service': 'Bhashini QoS Data Simulator',
                'version': '1.0.0',
                'endpoints': ['/health', '/status'],
                'status': 'running'
            })

    def connect_to_influxdb(self):
        """Establish connection to InfluxDB with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            logger.info(f"Attempting to connect to InfluxDB (attempt {attempt + 1}/{max_retries})")

            try:
                if self.influx_client.connect():
                    logger.info("Successfully connected to InfluxDB")
                    return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                logger.warning(f"Connection failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        logger.error("Failed to connect to InfluxDB after all retry attempts")
        return False

    def generate_and_write_metrics(self):
        """Generate metrics and write them to InfluxDB"""
        try:
            # Generate metrics batch
            metrics_batch = self.metrics_generator.generate_metrics_batch()
            
            # Write to InfluxDB
            if self.influx_client.write_metrics_batch(metrics_batch):
                self.metrics_count += len(metrics_batch)
                self.last_generation = datetime.now().isoformat()

                # Log summary
                summary = self.metrics_generator.get_metrics_summary()
                logger.info(f"Generated {len(metrics_batch)} metrics for {summary['services_count']} services and {summary['tenants_count']} tenants")

            else:
                logger.error("Failed to write metrics batch to InfluxDB")

        except Exception as e:
            logger.error(f"Error in generate_and_write_metrics: {str(e)}")

    def run_simulation(self):
        """Run the main simulation loop"""
        logger.info("Starting Bhashini QoS Data Simulator")

        # Start Flask health endpoint FIRST (before anything else)
        Thread(target=self.run_flask, daemon=True).start()
        
        # Wait a moment for Flask to start
        time.sleep(2)
        self.flask_started = True
        logger.info("Health endpoint started on port 8000")

        # Try to connect to InfluxDB (but don't fail if it doesn't work)
        influxdb_connected = self.connect_to_influxdb()
        if not influxdb_connected:
            logger.warning("InfluxDB connection failed, but continuing with health endpoint")
            # Keep running for health checks even without InfluxDB

        # Only start metrics generation if InfluxDB is connected
        if influxdb_connected:
            # Generate initial metrics
            logger.info("Generating initial metrics batch...")
            self.generate_and_write_metrics()

            self.running = True
            logger.info(f"Simulation started with {self.config.SIMULATION_INTERVAL}s interval")

            try:
                while self.running:
                    try:
                        # Generate metrics at regular intervals
                        self.generate_and_write_metrics()

                        # Sleep for the configured interval
                        time.sleep(self.config.SIMULATION_INTERVAL)

                    except Exception as e:
                        logger.error(f"Unexpected error in simulation loop: {str(e)}")
                        # Try to reconnect and continue
                        if not self.connect_to_influxdb():
                            logger.error("Failed to reconnect to InfluxDB, stopping simulation...")
                            break

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
            finally:
                self.shutdown()
        else:
            logger.info("Running in health-check only mode (no metrics generation)")
            # Keep the process running for health checks
            try:
                while True:
                    time.sleep(60)  # Sleep for 1 minute
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")

    def shutdown(self):
        """Gracefully shutdown the simulator"""
        logger.info("Shutting down Bhashini QoS Data Simulator...")
        self.running = False

        # Disconnect from InfluxDB
        try:
            self.influx_client.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting from InfluxDB: {e}")

        logger.info(f"Simulator shutdown complete. Total metrics generated: {self.metrics_count}")

    def run_flask(self):
        """Run Flask app for health checks"""
        try:
            logger.info("Starting Flask health endpoint on port 8000...")
            self.app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"Failed to start Flask health endpoint: {e}")
            self.flask_started = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    if hasattr(signal_handler, 'simulator'):
        signal_handler.simulator.shutdown()
    sys.exit(0)


def main():
    """Main entry point"""
    # Create simulator instance
    simulator = BhashiniQoSSimulator()
    signal_handler.simulator = simulator

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check if running in health check mode
    if len(sys.argv) > 1 and sys.argv[1] == '--health-check':
        simulator.run_flask()
    else:
        # Run simulation
        simulator.run_simulation()


if __name__ == "__main__":
    main()
