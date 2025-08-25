# Bhashini Provider Dashboard Guide

## Overview

The Bhashini Provider Dashboard is a comprehensive monitoring solution designed for the Bhashini operations team to monitor system health, track SLA compliance, and plan capacity across all customer tenants. This dashboard provides real-time insights into the performance of Translation, TTS, and ASR services across different SLA tiers.

## Dashboard Purpose and Scope

### Target Users
- **Bhashini Operations Team**: System administrators and DevOps engineers
- **Service Managers**: Team leads responsible for service delivery
- **Capacity Planners**: Engineers responsible for resource allocation

### Key Capabilities
- **Cross-Tenant Monitoring**: Aggregate metrics across all customer tenants
- **Service-Specific Filtering**: Focus on Translation, TTS, or ASR services
- **SLA Compliance Tracking**: Monitor adherence to service level agreements
- **Capacity Planning**: Analyze traffic patterns and resource utilization
- **Real-Time Alerts**: Immediate notification of system issues

## Dashboard Layout

### Header Section
The top row contains four key performance indicators:

1. **System Status**: Minimum availability across all services (color-coded thresholds)
2. **Total API Calls**: Sum of throughput across all tenants
3. **Active Tenants**: Count of currently active customer tenants
4. **System Health Score**: Overall system availability percentage

### Performance Overview Row
Two large panels showing service performance trends:

1. **Service Latency Trends**: Line chart showing P50 and P95 latency by service
2. **Error Rate Trends**: Line chart showing error rates over time

### Traffic Analysis Row
Two panels for traffic and availability monitoring:

1. **Throughput Patterns**: Bar chart showing API call volume by service
2. **Availability Heatmap**: Color-coded availability by service and SLA tier

### Capacity Planning Row
Three panels for resource management:

1. **Capacity Utilization**: Gauge showing current system load percentage
2. **SLA Compliance**: Count of services meeting 99% availability target
3. **Traffic Growth Trends**: Hourly traffic patterns for capacity planning

## Template Variables

### Service Filter
- **Name**: `service_name`
- **Type**: Multi-select dropdown
- **Options**: Translation, TTS, ASR
- **Usage**: Filter all panels to show data for specific services
- **Default**: All services selected

### SLA Tier Filter
- **Name**: `sla_tier`
- **Type**: Multi-select dropdown
- **Options**: Basic, Standard, Premium
- **Usage**: Filter data by SLA tier for compliance monitoring
- **Default**: All SLA tiers selected

### Time Range
- **Control**: Grafana time picker (top right)
- **Default**: Last 6 hours
- **Usage**: Adjust time range for historical analysis

## Metrics Interpretation

### Aggregate Metrics

#### Total API Calls
- **What it shows**: Sum of throughput across all tenants
- **How to read**: Higher numbers indicate more system usage
- **Action items**: 
  - Monitor for unusual spikes (potential DDoS)
  - Track growth trends for capacity planning

#### Average Response Times
- **What it shows**: Weighted average latency considering traffic volume
- **How to read**: Lower values indicate better performance
- **Thresholds**: 
  - Green: < 100ms
  - Yellow: 100-200ms
  - Red: > 200ms

#### Overall Error Rates
- **What it shows**: System-wide error percentage
- **How to read**: Lower values indicate better reliability
- **Thresholds**:
  - Green: < 1%
  - Yellow: 1-5%
  - Red: > 5%

#### System Availability
- **What it shows**: Minimum availability across all services
- **How to read**: Higher values indicate better uptime
- **SLA Targets**:
  - Basic: 95%
  - Standard: 99%
  - Premium: 99.9%

### Performance Metrics

#### Latency Percentiles
- **P50 (Median)**: 50% of requests complete within this time
- **P95**: 95% of requests complete within this time
- **P99**: 99% of requests complete within this time
- **Usage**: Identify performance outliers and bottlenecks

#### Error Rate Trends
- **Patterns to watch**:
  - Sudden spikes: Service deployment issues
  - Gradual increases: Performance degradation
  - Consistent high rates: Systemic problems

#### Throughput Patterns
- **Business hours**: Expect higher traffic during 9 AM - 6 PM
- **Peak times**: Monitor for capacity constraints
- **Off-hours**: Lower traffic, good for maintenance

## Operational Procedures

### Daily Monitoring Routine

#### Morning Check (9:00 AM)
1. **System Status**: Verify all services are green
2. **Error Rates**: Check for overnight issues
3. **Capacity**: Review overnight traffic patterns
4. **Alerts**: Address any overnight alerts

#### Midday Review (2:00 PM)
1. **Performance**: Check latency trends during peak hours
2. **Traffic**: Monitor for unusual spikes
3. **Availability**: Ensure SLA compliance

#### Evening Summary (6:00 PM)
1. **Daily Summary**: Review overall performance
2. **Issues Log**: Document any problems encountered
3. **Capacity Planning**: Note any capacity constraints

### Weekly Capacity Planning Review

#### Monday Morning
1. **Weekend Analysis**: Review weekend traffic patterns
2. **Capacity Trends**: Identify growth patterns
3. **Resource Planning**: Plan for upcoming week

#### Friday Afternoon
1. **Weekly Summary**: Compile performance metrics
2. **SLA Report**: Generate compliance report
3. **Next Week Planning**: Identify potential issues

### Monthly Performance Analysis

#### First Week of Month
1. **Monthly Report**: Compile comprehensive metrics
2. **Trend Analysis**: Identify long-term patterns
3. **Capacity Projections**: Plan for next month
4. **SLA Review**: Assess compliance across all tiers

## Troubleshooting Guide

### Common Dashboard Issues

#### No Data Displayed
1. **Check Data Source**: Verify InfluxDB connection
2. **Time Range**: Ensure time range includes data
3. **Filters**: Check if template variables are too restrictive
4. **Service Status**: Verify data simulator is running

#### Slow Dashboard Loading
1. **Query Optimization**: Check Flux query performance
2. **Time Range**: Reduce time range for faster loading
3. **Data Volume**: Consider data retention policies
4. **Grafana Resources**: Check Grafana container resources

#### Incorrect Metrics
1. **Data Validation**: Verify data simulator output
2. **Query Logic**: Review Flux query calculations
3. **Units**: Check metric units and conversions
4. **Aggregation**: Verify aggregation functions

### Performance Optimization

#### Query Optimization
1. **Time Ranges**: Use appropriate time windows
2. **Filtering**: Apply filters early in query pipeline
3. **Grouping**: Minimize unnecessary grouping operations
4. **Window Functions**: Use reasonable aggregation intervals

#### Dashboard Optimization
1. **Panel Count**: Limit panels per dashboard
2. **Refresh Rates**: Set appropriate refresh intervals
3. **Data Sources**: Use optimized data source queries
4. **Caching**: Leverage Grafana query caching

## Customization Options

### Adding New Panels

#### Stat Panel Example
```json
{
  "id": 12,
  "title": "Custom Metric",
  "type": "stat",
  "targets": [{
    "refId": "A",
    "query": "your_flux_query_here",
    "datasource": {
      "type": "influxdb",
      "uid": "InfluxDB-Provider-CrossTenant"
    }
  }]
}
```

#### Time Series Panel Example
```json
{
  "id": 13,
  "title": "Custom Trend",
  "type": "timeseries",
  "targets": [{
    "refId": "A",
    "query": "your_flux_query_here",
    "datasource": {
      "type": "influxdb",
      "uid": "InfluxDB-Provider-CrossTenant"
    }
  }]
}
```

### Modifying Existing Panels

#### Changing Queries
1. **Edit Panel**: Click panel title → Edit
2. **Modify Query**: Update Flux query in query editor
3. **Test Query**: Use query inspector to validate
4. **Save Changes**: Apply and save panel

#### Adjusting Thresholds
1. **Panel Settings**: Open panel edit mode
2. **Field Config**: Navigate to field configuration
3. **Thresholds**: Modify color thresholds
4. **Units**: Adjust display units as needed

### Creating Derived Dashboards

#### Service-Specific Dashboards
1. **Copy Dashboard**: Duplicate existing dashboard
2. **Modify Filters**: Adjust template variables
3. **Customize Panels**: Add service-specific metrics
4. **Save As**: Save with descriptive name

#### SLA Tier Dashboards
1. **Filter by SLA**: Use SLA tier template variable
2. **Focus Metrics**: Include SLA-specific thresholds
3. **Compliance Tracking**: Add compliance panels
4. **Alerting**: Configure SLA-specific alerts

## Alert Configuration

### Setting Up Alerts

#### Availability Alerts
1. **Panel Alerts**: Configure alerts on availability panels
2. **Thresholds**: Set alert thresholds (e.g., < 99%)
3. **Notification**: Configure notification channels
4. **Escalation**: Set up escalation policies

#### Performance Alerts
1. **Latency Alerts**: Alert on high latency (P95 > 200ms)
2. **Error Rate Alerts**: Alert on high error rates (> 5%)
3. **Capacity Alerts**: Alert on high utilization (> 90%)

### Alert Channels

#### Email Notifications
1. **SMTP Configuration**: Configure email server
2. **Recipient Lists**: Set up distribution lists
3. **Template**: Customize alert message format
4. **Frequency**: Set alert frequency limits

#### Slack Integration
1. **Webhook Setup**: Configure Slack webhook
2. **Channel Selection**: Choose notification channels
3. **Message Format**: Customize Slack message format
4. **User Mentions**: Set up user notifications

## Maintenance and Updates

### Regular Maintenance

#### Weekly Tasks
1. **Dashboard Review**: Check for broken queries
2. **Performance Check**: Monitor dashboard load times
3. **Data Validation**: Verify data accuracy
4. **User Access**: Review user permissions

#### Monthly Tasks
1. **Query Optimization**: Review and optimize Flux queries
2. **Panel Updates**: Update outdated panels
3. **Documentation**: Update this guide
4. **User Training**: Conduct user training sessions

### Version Control

#### Dashboard Changes
1. **Git Integration**: Version control dashboard changes
2. **Change Log**: Document all modifications
3. **Testing**: Test changes in development environment
4. **Deployment**: Deploy to production environment

#### Backup and Recovery
1. **Regular Backups**: Export dashboard configurations
2. **Version History**: Maintain change history
3. **Recovery Plan**: Document recovery procedures
4. **Testing**: Test recovery procedures regularly

## Support and Resources

### Documentation Links
- [Grafana Documentation](https://grafana.com/docs/)
- [InfluxDB Flux Documentation](https://docs.influxdata.com/flux/)
- [Bhashini Project Wiki](internal-link)

### Contact Information
- **Operations Team**: ops@bhashini.com
- **DevOps Team**: devops@bhashini.com
- **Emergency Contact**: oncall@bhashini.com

### Training Resources
- **Dashboard Tutorial**: Available in company LMS
- **Flux Query Guide**: Internal documentation
- **Best Practices**: Monthly training sessions
- **User Community**: Internal Slack channel

---

*Last Updated: August 2025*
*Version: 1.0*
*Author: Bhashini DevOps Team*
