// Bhashini Provider Dashboard Flux Query Templates
// This file contains optimized Flux queries for cross-tenant provider monitoring

// =============================================================================
// AGGREGATE METRICS QUERIES
// =============================================================================

// Total API calls across all tenants
// Usage: Sum of throughput across all tenants for capacity planning
total_api_calls = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group()
    |> sum()
    |> yield(name: "total_calls")

// Weighted average latency by traffic volume
// Usage: More accurate performance indicator considering traffic distribution
weighted_avg_latency = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["tenant_id", "service_name"])
    |> mean()
    |> group()
    |> weightedMean(column: "_value", weight: "throughput")
    |> yield(name: "weighted_latency")

// Overall error rate aggregation
// Usage: System-wide error rate for health monitoring
overall_error_rate = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "error_rate")
    |> group()
    |> mean()
    |> yield(name: "overall_error_rate")

// System-wide availability metrics
// Usage: Minimum availability across all services for SLA compliance
system_availability = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["tenant_id", "service_name"])
    |> mean()
    |> group()
    |> min()
    |> yield(name: "min_availability")

// =============================================================================
// SERVICE-SPECIFIC QUERIES
// =============================================================================

// Latency percentiles (P50, P95, P99) by service type
// Usage: Performance monitoring with service filtering
service_latency_percentiles = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.50)
    |> yield(name: "p50")

service_latency_p95 = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.95)
    |> yield(name: "p95")

service_latency_p99 = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.99)
    |> yield(name: "p99")

// Error rate trends with service filtering
// Usage: Service-specific error monitoring
service_error_rate_trends = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "error_rate")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "error_rate")

// Throughput patterns with time-based grouping
// Usage: Traffic analysis and capacity planning
service_throughput_patterns = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)
    |> yield(name: "throughput")

// Availability tracking by service and SLA tier
// Usage: SLA compliance monitoring
service_availability_tracking = (service_filter) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))
    |> group(columns: ["service_name", "sla_tier"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "availability")

// =============================================================================
// CAPACITY PLANNING QUERIES
// =============================================================================

// Traffic growth rate calculations
// Usage: Capacity planning and resource allocation
traffic_growth_rate = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
    |> yield(name: "hourly_traffic")

// Capacity utilization metrics
// Usage: Resource utilization monitoring
capacity_utilization = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group()
    |> sum()
    |> map(fn: (r) => ({r with _value: r._value / 1000.0}))
    |> yield(name: "capacity_utilization")

// Peak traffic analysis
// Usage: Capacity planning and peak load management
peak_traffic_analysis = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: 15m, fn: sum, createEmpty: false)
    |> group()
    |> max()
    |> yield(name: "peak_traffic")

// Resource allocation by service type
// Usage: Resource distribution analysis
resource_allocation_by_service = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> sum()
    |> yield(name: "service_allocation")

// =============================================================================
// TEMPLATE VARIABLE QUERIES
// =============================================================================

// Service name extraction for dropdown filters
// Usage: Dynamic service filtering
service_names_for_filter = () =>
  from(bucket: "qos_metrics")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> group(columns: ["service_name"])
    |> distinct(column: "service_name")
    |> yield(name: "service_names")

// SLA tier enumeration
// Usage: SLA tier filtering
sla_tiers_for_filter = () =>
  from(bucket: "qos_metrics")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> group(columns: ["sla_tier"])
    |> distinct(column: "sla_tier")
    |> yield(name: "sla_tiers")

// Tenant list generation
// Usage: Tenant-specific filtering
tenant_list_for_filter = () =>
  from(bucket: "qos_metrics")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> group(columns: ["tenant_id"])
    |> distinct(column: "tenant_id")
    |> yield(name: "tenant_list")

// =============================================================================
// PERFORMANCE ANALYSIS QUERIES
// =============================================================================

// Cross-tenant performance comparisons
// Usage: Performance benchmarking across tenants
cross_tenant_performance = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["tenant_id", "service_name"])
    |> mean()
    |> group(columns: ["tenant_id"])
    |> mean()
    |> yield(name: "tenant_performance")

// SLA compliance calculations
// Usage: SLA compliance tracking
sla_compliance_tracking = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["tenant_id", "service_name", "sla_tier"])
    |> mean()
    |> filter(fn: (r) => r._value >= 99.0)
    |> count()
    |> yield(name: "sla_compliant")

// Traffic pattern analysis
// Usage: Business hours vs off-hours analysis
traffic_pattern_analysis = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
    |> yield(name: "hourly_patterns")

// Operational insights
// Usage: Top performing services and underperforming areas
top_performing_services = () =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["service_name"])
    |> mean()
    |> sort(columns: ["_value"], desc: true)
    |> limit(n: 5)
    |> yield(name: "top_services")

// =============================================================================
// QUERY OPTIMIZATION NOTES
// =============================================================================

// Performance Considerations:
// 1. Use appropriate time ranges to limit data processing
// 2. Group operations should be minimized and strategic
// 3. Window functions should use reasonable intervals
// 4. Filter operations should be applied early in the pipeline
// 5. Use yield() for clear output naming

// Variable Substitution:
// - ${service_name:json} for service filtering
// - ${time_range} for dynamic time ranges
// - ${sla_tier} for SLA tier filtering
// - v.timeRangeStart/v.timeRangeStop for Grafana time picker
// - v.windowPeriod for dynamic window sizing
