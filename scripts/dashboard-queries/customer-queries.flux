// Bhashini Customer Dashboard Flux Query Templates
// This file contains tenant-isolated Flux queries for customer-specific monitoring
// All queries automatically filter by tenant_id to ensure complete data isolation

// =============================================================================
// TENANT-ISOLATED BASE QUERIES
// =============================================================================

// Base query template with tenant isolation
// Usage: Foundation for all customer queries with automatic tenant filtering
base_tenant_query = (tenant_id) =>
  from(bucket: "qos_metrics")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
    |> filter(fn: (r) => r["tenant_id"] == tenant_id)

// Service-filtered base query
// Usage: Base query with both tenant and service filtering
base_service_query = (tenant_id, service_filter) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => contains(value: r["service_name"], set: service_filter))

// =============================================================================
// API RESPONSE TIME QUERIES
// =============================================================================

// P50 latency by service type for specific tenant
// Usage: Performance monitoring with tenant isolation
customer_p50_latency = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.50, method: "estimate_tdigest")
    |> yield(name: "p50_latency")

// P95 latency by service type for specific tenant
// Usage: High percentile performance monitoring
customer_p95_latency = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.95, method: "estimate_tdigest")
    |> yield(name: "p95_latency")

// P99 latency by service type for specific tenant
// Usage: Extreme percentile performance monitoring
customer_p99_latency = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.99, method: "estimate_tdigest")
    |> yield(name: "p99_latency")

// Average latency trend for tenant
// Usage: Overall performance trend analysis
customer_avg_latency_trend = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "latency")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "avg_latency_trend")

// =============================================================================
// ERROR RATE ANALYSIS QUERIES
// =============================================================================

// Error rate by service for specific tenant
// Usage: Service-specific error monitoring
customer_error_rate_by_service = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "error_rate")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "error_rate_by_service")

// Error rate trend over time for tenant
// Usage: Error rate pattern analysis
customer_error_rate_trend = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "error_rate")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "error_rate_trend")

// Error rate distribution by service type
// Usage: Error rate comparison across services
customer_error_rate_distribution = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "error_rate")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "error_rate_distribution")

// =============================================================================
// SLA COMPLIANCE TRACKING QUERIES
// =============================================================================

// Availability percentage for tenant
// Usage: SLA compliance monitoring
customer_availability = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> map(fn: (r) => ({r with _value: r._value * 100.0}))
    |> yield(name: "availability_percentage")

// SLA compliance status based on tier
// Usage: SLA breach detection and compliance tracking
customer_sla_compliance = (tenant_id, sla_tier) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> map(fn: (r) => ({
      r with 
      sla_threshold: if sla_tier == "premium" then 99.9 
                     else if sla_tier == "standard" then 99.5 
                     else 99.0,
      compliance_status: if r._value >= (if sla_tier == "premium" then 0.999 
                                        else if sla_tier == "standard" then 0.995 
                                        else 0.99) then "compliant" else "breach"
    }))
    |> yield(name: "sla_compliance")

// SLA compliance percentage over time
// Usage: Historical compliance tracking
customer_sla_compliance_trend = (tenant_id, sla_tier) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> map(fn: (r) => ({
      r with 
      sla_threshold: if sla_tier == "premium" then 99.9 
                     else if sla_tier == "standard" then 99.5 
                     else 99.0,
      compliance_percentage: if r._value >= (if sla_tier == "premium" then 0.999 
                                            else if sla_tier == "standard" then 0.995 
                                            else 0.99) then 100.0 else (r._value * 100.0)
    }))
    |> yield(name: "sla_compliance_trend")

// =============================================================================
// USAGE ANALYTICS QUERIES
// =============================================================================

// API call volume for tenant
// Usage: Usage tracking and capacity planning
customer_api_volume = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)
    |> yield(name: "api_call_volume")

// Throughput trend for tenant
// Usage: Usage pattern analysis
customer_throughput_trend = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "throughput_trend")

// Service usage distribution for tenant
// Usage: Service popularity analysis
customer_service_usage_distribution = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)
    |> yield(name: "service_usage_distribution")

// Peak usage detection for tenant
// Usage: Capacity planning and peak analysis
customer_peak_usage = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> filter(fn: (r) => r["metric_type"] == "throughput")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: max, createEmpty: false)
    |> yield(name: "peak_usage")

// =============================================================================
// SERVICE PERFORMANCE BREAKDOWN QUERIES
// =============================================================================

// Translation service performance for tenant
// Usage: Translation-specific monitoring
customer_translation_performance = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["service_name"] == "Translation")
    |> group(columns: ["metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "translation_performance")

// TTS service performance for tenant
// Usage: TTS-specific monitoring
customer_tts_performance = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["service_name"] == "TTS")
    |> group(columns: ["metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "tts_performance")

// ASR service performance for tenant
// Usage: ASR-specific monitoring
customer_asr_performance = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["service_name"] == "ASR")
    |> group(columns: ["metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "asr_performance")

// Service comparison within tenant
// Usage: Cross-service performance analysis
customer_service_comparison = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> group(columns: ["service_name", "metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "service_comparison")

// =============================================================================
// TEMPLATE VARIABLE QUERIES
// =============================================================================

// Extract service names for tenant
// Usage: Service filter template variable
customer_services = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> group(columns: ["service_name"])
    |> distinct(column: "service_name")
    |> yield(name: "available_services")

// Extract metric types for tenant
// Usage: Metric type filter template variable
customer_metric_types = (tenant_id) =>
  base_tenant_query(tenant_id: tenant_id)
    |> group(columns: ["metric_type"])
    |> distinct(column: "metric_type")
    |> yield(name: "available_metrics")

// SLA tier information for tenant
// Usage: SLA tier display and threshold configuration
customer_sla_info = (tenant_id, sla_tier) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group()
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> map(fn: (r) => ({
      r with 
      tenant_id: tenant_id,
      sla_tier: sla_tier,
      availability_threshold: if sla_tier == "premium" then 99.9 
                              else if sla_tier == "standard" then 99.5 
                              else 99.0,
      latency_threshold: if sla_tier == "premium" then 100.0 
                         else if sla_tier == "standard" then 200.0 
                         else 500.0,
      error_rate_threshold: if sla_tier == "premium" then 0.1 
                           else if sla_tier == "standard" then 0.5 
                           else 1.0
    }))
    |> yield(name: "sla_information")

// =============================================================================
// COMPOSITE QUERIES FOR DASHBOARD PANELS
// =============================================================================

// Complete service overview for tenant
// Usage: Main dashboard overview panel
customer_service_overview = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> group(columns: ["service_name", "metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> pivot(rowKey:["_time"], columnKey: ["metric_type"], valueColumn: "_value")
    |> yield(name: "service_overview")

// SLA compliance summary for tenant
// Usage: SLA compliance dashboard panel
customer_sla_summary = (tenant_id, sla_tier) =>
  base_tenant_query(tenant_id: tenant_id)
    |> filter(fn: (r) => r["metric_type"] == "availability")
    |> group(columns: ["service_name"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> map(fn: (r) => ({
      r with 
      sla_threshold: if sla_tier == "premium" then 0.999 
                     else if sla_tier == "standard" then 0.995 
                     else 0.99,
      compliance_percentage: if r._value >= (if sla_tier == "premium" then 0.999 
                                            else if sla_tier == "standard" then 0.995 
                                            else 0.99) then 100.0 else (r._value * 100.0),
      status: if r._value >= (if sla_tier == "premium" then 0.999 
                              else if sla_tier == "standard" then 0.995 
                              else 0.99) then "compliant" else "breach"
    }))
    |> yield(name: "sla_summary")

// Performance trends for tenant
// Usage: Performance trend dashboard panel
customer_performance_trends = (tenant_id, service_filter) =>
  base_service_query(tenant_id: tenant_id, service_filter: service_filter)
    |> group(columns: ["service_name", "metric_type"])
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> yield(name: "performance_trends")
