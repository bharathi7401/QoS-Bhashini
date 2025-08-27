# 📊 Dashboard Formatting Rules & Enforcement

## 🚫 NEVER DO (Will Block Commits)

### ❌ **Panel Titles**
- **Don't put units in titles**: `"System Status (%)"` → `"System Status"`
- **Don't use technical terms**: `"Raw Data Object"` → `"System Data"`
- **Don't use placeholder text**: `"Pie Chart Slice"` → `"SLA Tier Distribution"`

### ❌ **Data Exposure**
- **Don't expose raw data objects**: `_value { ... }` → Clean numeric values
- **Don't show technical field names**: `_measurement`, `_field`, `_value` → Human-readable names
- **Don't skip data transformation**: Always use `map()` functions

### ❌ **Field Configuration**
- **Don't skip displayName**: Every panel MUST have `displayName` in `fieldConfig.defaults`
- **Don't skip unit configuration**: Every panel MUST have `unit` in `fieldConfig.defaults`
- **Don't use technical display names**: `displayName: "_value"` → `displayName: "Availability"`

## ✅ ALWAYS DO (Required for Commits)

### ✅ **Panel Titles**
- **Use clean, descriptive titles**: `"System Status"`, `"Customer Performance"`
- **Keep titles business-friendly**: Focus on what the metric represents
- **Use consistent naming**: Follow established patterns across dashboards

### ✅ **Data Transformation**
- **Always use map() functions**: Transform raw data into clean, structured output
- **Map to human-readable fields**: `metric: "Availability"`, `tenant: "Enterprise 1"`
- **Structure output consistently**: Use the same field names across similar panels

### ✅ **Field Configuration**
- **Always include displayName**: `"displayName": "Human Readable Name"`
- **Always include unit**: `"unit": "percent"`, `"unit": "ms"`, `"unit": "requests_per_minute"`
- **Use proper thresholds**: Color-code based on SLA requirements
- **Set appropriate color modes**: `"color": {"mode": "thresholds"}` for KPIs

## 🔍 **Validation & Enforcement**

### **Automatic Validation**
Our system automatically validates ALL dashboard changes:

1. **Pre-commit Hook**: Blocks commits with formatting violations
2. **CI/CD Pipeline**: Validates on every push and pull request
3. **Real-time Scripts**: Manual validation anytime with `./scripts/validate-dashboard-format.sh`

### **Validation Commands**
```bash
# Quick validation (recommended before commits)
./scripts/validate-dashboard-format.sh

# Detailed Python validation
python scripts/test_dashboard_format.py

# Check specific dashboard
./scripts/validate-dashboard-format.sh grafana/provisioning/dashboards/your-dashboard.json
```

### **What Gets Checked**
- ✅ No units in panel titles
- ✅ All panels have displayName
- ✅ Flux queries use map() functions
- ✅ Proper unit configuration
- ✅ Clean, business-friendly field names
- ✅ No technical terms exposed to users
- ✅ Consistent data structure

## 📋 **Common Fixes**

### **Fix 1: Units in Titles**
```json
// ❌ WRONG
"title": "System Availability (%)"

// ✅ CORRECT
"title": "System Availability",
"fieldConfig": {
  "defaults": {
    "unit": "percent"
  }
}
```

### **Fix 2: Missing map() Function**
```json
// ❌ WRONG
"query": "from(bucket: \"qos_metrics\") |> filter(...) |> mean()"

// ✅ CORRECT
"query": "from(bucket: \"qos_metrics\") |> filter(...) |> mean() |> map(fn: (r) => ({ _value: r._value, metric: \"Availability\" }))"
```

### **Fix 3: Missing displayName**
```json
// ❌ WRONG
"fieldConfig": {
  "defaults": {
    "unit": "percent"
  }
}

// ✅ CORRECT
"fieldConfig": {
  "defaults": {
    "unit": "percent",
    "displayName": "Availability"
  }
}
```

### **Fix 4: Technical Field Names**
```json
// ❌ WRONG
"displayName": "_value"

// ✅ CORRECT
"displayName": "Response Time"
```

## 🚀 **Best Practices**

### **Panel Structure**
```json
{
  "id": null,
  "title": "Clean Business Title",
  "type": "stat",
  "targets": [
    {
      "refId": "A",
      "query": "Flux query with map() function",
      "datasource": {"type": "influxdb", "uid": "influxdb-working"}
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "unit": "appropriate_unit",
      "thresholds": {"steps": [...]},
      "displayName": "Human Readable Name"
    }
  }
}
```

### **Naming Conventions**
- **Panels**: `"Customer Performance"`, `"System Health"`, `"SLA Compliance"`
- **Fields**: `"availability"`, `"response_time"`, `"error_rate"`
- **Units**: `"percent"`, `"ms"`, `"requests_per_minute"`, `"none"`

### **Data Transformation Pattern**
```flux
from(bucket: "qos_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["metric_type"] == "availability")
  |> group()
  |> mean()
  |> map(fn: (r) => ({
      _time: r._time,
      _value: r._value,
      metric: "Availability",
      status: if r._value >= 99.0 then "Excellent" else if r._value >= 95.0 then "Good" else "Poor"
    }))
```

## 🔧 **Troubleshooting**

### **Common Error Messages**
- **"Units found in panel titles"**: Remove units from titles, add to fieldConfig
- **"Missing displayName"**: Add displayName to fieldConfig.defaults
- **"Missing map() function"**: Add map() transformation to Flux queries
- **"Technical field names exposed"**: Use human-readable names in displayName

### **Getting Help**
1. **Run validation**: `./scripts/validate-dashboard-format.sh`
2. **Check templates**: `templates/dashboard-panel-template.json`
3. **Review examples**: Look at existing working dashboards
4. **Ask team**: Dashboard formatting is everyone's responsibility

## 📚 **Resources**

- **Template**: `templates/dashboard-panel-template.json`
- **Validation Scripts**: `scripts/validate-dashboard-format.sh`, `scripts/test_dashboard_format.py`
- **CI/CD**: `.github/workflows/dashboard-validation.yml`
- **Pre-commit Hook**: `.git/hooks/pre-commit`

---

**Remember**: These rules are automatically enforced. Following them ensures your dashboards are business-ready and maintainable! 🎯
