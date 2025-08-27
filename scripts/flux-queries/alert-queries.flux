import "experimental"

availability = (tenant) =>
  from(bucket: "qos_metrics")
    |> range(start: -5m)
    |> filter(fn: (r) => r._measurement == "qos_metrics" and r.metric_type == "availability" and r.tenant_id == tenant)
    |> mean()
    |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))
    |> last()

p95_latency = (tenant) =>
  from(bucket: "qos_metrics")
    |> range(start: -5m)
    |> filter(fn: (r) => r._measurement == "qos_metrics" and r.metric_type == "latency" and r.tenant_id == tenant)
    |> aggregateWindow(every: 1m, fn: quantile, q: 0.95, method: "estimate_tdigest")
    |> last()
