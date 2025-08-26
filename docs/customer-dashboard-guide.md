# Bhashini Customer Dashboard Guide

## Overview

This guide provides comprehensive information about setting up, using, and managing customer-specific dashboards in the Bhashini QoS monitoring system. Customer dashboards provide isolated, tenant-specific monitoring capabilities with SLA compliance tracking and performance analytics.

## Table of Contents

1. [Customer Dashboard Overview](#customer-dashboard-overview)
2. [Dashboard Features](#dashboard-features)
3. [Data Isolation and Security](#data-isolation-and-security)
4. [SLA Compliance Tracking](#sla-compliance-tracking)
5. [API Performance Monitoring](#api-performance-monitoring)
6. [Error Rate Analysis](#error-rate-analysis)
7. [Usage Analytics](#usage-analytics)
8. [Dashboard Navigation](#dashboard-navigation)
9. [Customer Onboarding](#customer-onboarding)
10. [Troubleshooting](#troubleshooting)
11. [Customization and Extensions](#customization-and-extensions)

## Customer Dashboard Overview

### Purpose and Scope

Customer dashboards provide isolated monitoring capabilities for each customer organization, allowing them to:

- Monitor their own API performance and service health
- Track SLA compliance based on their service tier
- Analyze usage patterns and trends
- Receive alerts for performance issues
- Access historical data for capacity planning

### Target Users

- **Customer Administrators**: Full access to dashboard configuration and user management
- **Customer End Users**: View-only access to monitoring data and reports
- **Customer Support Teams**: Access to performance metrics for troubleshooting

### Key Capabilities

- **Service Monitoring**: Real-time monitoring of Translation, TTS, and ASR services
- **SLA Tracking**: Automatic compliance monitoring based on customer tier
- **Performance Analytics**: P50, P95, P99 latency percentiles and trends
- **Error Rate Monitoring**: Service-specific error tracking and alerting
- **Usage Analytics**: API call volume, throughput, and peak usage analysis

### Differences from Provider Dashboards

| Feature | Customer Dashboard | Provider Dashboard |
|---------|-------------------|-------------------|
| Data Scope | Tenant-specific only | Cross-tenant aggregated |
| SLA Tracking | Customer-specific thresholds | System-wide compliance |
| User Access | Customer organization only | Provider organization |
| Customization | Limited to customer tier | Full provider control |
| Data Retention | Customer tier dependent | Provider policy |

## Dashboard Features

### Header Section

The dashboard header displays:
- **Customer Name**: Organization identifier
- **Current SLA Tier**: Premium, Standard, or Basic
- **Overall Service Health**: Color-coded status indicator
- **Last Updated**: Timestamp of most recent data refresh

### Key Performance Indicators (KPIs)

#### Current Response Time
- Average latency across all services
- Color-coded based on SLA thresholds
- Real-time updates every 30 seconds

#### Current Error Rate
- Percentage of failed API calls
- Threshold-based alerting
- Service-specific breakdown available

#### API Calls (Last Hour)
- Total API requests in the past hour
- Service-specific volume tracking
- Trend comparison with previous periods

#### SLA Compliance Status
- Current compliance percentage
- SLA tier-specific thresholds
- Breach detection and alerting

### API Response Time Analysis

#### P50, P95, P99 Latency Trends
- **P50**: Median response time (50th percentile)
- **P95**: 95th percentile response time
- **P99**: 99th percentile response time (extreme cases)

#### Service-Specific Performance
- Individual service monitoring (Translation, TTS, ASR)
- Trend analysis over configurable time ranges
- Threshold lines based on SLA requirements

#### Performance Thresholds by SLA Tier

| SLA Tier | P50 Target | P95 Target | P99 Target |
|-----------|------------|------------|------------|
| Premium   | ≤100ms     | ≤200ms     | ≤500ms     |
| Standard  | ≤200ms     | ≤400ms     | ≤1000ms    |
| Basic     | ≤500ms     | ≤1000ms    | ≤2000ms    |

### Error Rate Monitoring

#### Service-Specific Error Rates
- Individual service error tracking
- Real-time error rate calculation
- Historical trend analysis

#### Error Rate Thresholds

| SLA Tier | Warning Threshold | Critical Threshold |
|-----------|-------------------|-------------------|
| Premium   | 0.1%             | 0.5%             |
| Standard  | 0.5%             | 1.0%             |
| Basic     | 1.0%             | 2.0%             |

#### Error Rate Analysis
- Error pattern identification
- Service comparison
- Peak error time detection

### SLA Compliance Tracking

#### Availability Monitoring
- Real-time availability percentage
- SLA threshold comparison
- Compliance trend analysis

#### SLA Thresholds by Tier

| SLA Tier | Availability Target | Uptime per Month |
|-----------|-------------------|------------------|
| Premium   | 99.9%             | 43.2 minutes downtime |
| Standard  | 99.5%             | 3.6 hours downtime   |
| Basic     | 99.0%             | 7.2 hours downtime   |

#### Compliance Reporting
- Historical compliance data
- SLA breach incidents
- Compliance percentage trends

### Usage Analytics

#### API Call Volume Trends
- Hourly, daily, and monthly trends
- Service-specific usage patterns
- Peak usage identification

#### Service Usage Distribution
- Pie chart showing service popularity
- Usage percentage by service
- Capacity planning insights

#### Peak Usage Analysis
- Peak load identification
- Usage pattern recognition
- Capacity planning recommendations

### Service Performance Breakdown

#### Translation Service
- Dedicated performance metrics
- SLA compliance indicators
- Performance trend analysis

#### TTS Service
- Text-to-Speech specific monitoring
- Audio processing metrics
- Quality and performance tracking

#### ASR Service
- Speech recognition monitoring
- Accuracy and performance metrics
- Processing time analysis

## Data Isolation and Security

### Tenant Isolation Mechanism

Customer dashboards use **tag-based data isolation** to ensure complete data separation:

```flux
// All queries automatically filter by tenant_id
from(bucket: "qos_metrics")
  |> filter(fn: (r) => r["tenant_id"] == "enterprise_1")
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
```

### Security Measures

#### Authentication
- **Organization-Level Access**: Customers can only access their own organization
- **User Role Management**: Admin, Editor, and Viewer roles
- **API Key Restrictions**: Tenant-specific API keys with read-only access

#### Data Access Controls
- **Bucket Permissions**: Tenant-specific bucket access
- **Query Filtering**: Automatic tenant_id injection in all queries
- **Cross-Tenant Prevention**: No possibility of data leakage between customers

#### Data Retention Policies

| SLA Tier | Data Retention | Backup Frequency |
|-----------|----------------|------------------|
| Premium   | 90 days        | Daily            |
| Standard  | 60 days        | Weekly           |
| Basic     | 30 days        | Monthly          |

### Access Control Matrix

| Role | Dashboard View | Data Export | Configuration | User Management |
|------|----------------|--------------|---------------|-----------------|
| Admin | Full | Yes | Yes | Yes |
| Editor | Full | Yes | Limited | No |
| Viewer | Read-only | No | No | No |

## SLA Compliance Tracking

### How SLA Thresholds Work

SLA thresholds are automatically configured based on customer tier:

1. **Premium Customers**: 99.9% availability, 100ms P95 latency
2. **Standard Customers**: 99.5% availability, 200ms P95 latency  
3. **Basic Customers**: 99.0% availability, 500ms P95 latency

### Availability Monitoring

#### Real-Time Calculation
```flux
// Availability percentage calculation
availability_percentage = (successful_requests / total_requests) * 100
```

#### SLA Breach Detection
- Automatic threshold violation detection
- Real-time alerting for compliance issues
- Historical breach tracking and reporting

#### Compliance Percentage
- Rolling compliance calculation
- Monthly compliance summaries
- Trend analysis for improvement planning

### SLA Reporting

#### Daily Reports
- 24-hour compliance summary
- Breach incidents and duration
- Performance trend analysis

#### Monthly Reports
- Monthly compliance percentage
- SLA breach summary
- Performance improvement recommendations

## API Performance Monitoring

### Understanding Response Time Percentiles

#### P50 (Median)
- **Definition**: 50% of requests complete within this time
- **Use Case**: Typical performance expectation
- **Example**: P50 = 150ms means half of requests complete in ≤150ms

#### P95 (95th Percentile)
- **Definition**: 95% of requests complete within this time
- **Use Case**: Performance guarantee for most users
- **Example**: P95 = 300ms means 95% of requests complete in ≤300ms

#### P99 (99th Percentile)
- **Definition**: 99% of requests complete within this time
- **Use Case**: Extreme case performance
- **Example**: P99 = 800ms means 99% of requests complete in ≤800ms

### Interpreting Latency Trends

#### Normal Patterns
- **Stable Performance**: Consistent latency with minor variations
- **Daily Patterns**: Peak usage times showing higher latency
- **Weekly Patterns**: Weekend vs. weekday differences

#### Performance Issues
- **Spikes**: Sudden latency increases indicating problems
- **Degradation**: Gradual performance decline over time
- **Service Differences**: One service performing worse than others

### Performance Optimization Recommendations

#### High P95/P99 Latency
- Check service resource utilization
- Review database query performance
- Investigate network latency issues

#### Increasing Trend
- Monitor resource consumption
- Check for memory leaks
- Review recent code deployments

## Error Rate Analysis

### Error Rate Calculation

#### Formula
```flux
error_rate = (failed_requests / total_requests) * 100
```

#### Real-Time Monitoring
- Continuous error rate calculation
- Rolling window averaging
- Threshold-based alerting

### Error Rate Patterns

#### Common Patterns
- **Spikes**: Sudden error rate increases
- **Service-Specific**: Errors concentrated in one service
- **Time-Based**: Errors occurring at specific times

#### Root Cause Analysis
- **Service Dependencies**: Database or external service issues
- **Resource Constraints**: Memory, CPU, or network problems
- **Configuration Issues**: Incorrect settings or parameters

### Error Rate Thresholds

#### Warning Levels
- **Premium**: 0.1% (1 error per 1000 requests)
- **Standard**: 0.5% (5 errors per 1000 requests)
- **Basic**: 1.0% (10 errors per 1000 requests)

#### Critical Levels
- **Premium**: 0.5% (5 errors per 1000 requests)
- **Standard**: 1.0% (10 errors per 1000 requests)
- **Basic**: 2.0% (20 errors per 1000 requests)

## Usage Analytics

### API Call Volume Tracking

#### Metrics Available
- **Total API Calls**: Overall request volume
- **Service Breakdown**: Calls per service type
- **Time Patterns**: Hourly, daily, monthly trends

#### Volume Analysis
- **Peak Usage**: Highest traffic periods
- **Usage Patterns**: Regular vs. irregular patterns
- **Growth Trends**: Volume increase over time

### Throughput Analysis

#### Throughput Metrics
- **Requests per Second**: Real-time throughput
- **Peak Throughput**: Maximum observed throughput
- **Average Throughput**: Typical throughput levels

#### Capacity Planning
- **Current Utilization**: How much capacity is used
- **Peak Planning**: Preparing for maximum loads
- **Scaling Decisions**: When to add resources

### Service Usage Distribution

#### Popular Services
- **Most Used**: Services with highest call volume
- **Usage Patterns**: How services are used together
- **Growth Trends**: Which services are growing fastest

#### Business Insights
- **Feature Adoption**: Which services are most popular
- **User Behavior**: How customers use the platform
- **Revenue Impact**: Service usage correlation with business metrics

## Dashboard Navigation

### Template Variables

#### Service Filter
- **Purpose**: Filter dashboard data by service type
- **Options**: Translation, TTS, ASR, or All Services
- **Usage**: Select specific services or view all together
- **Refresh**: Updates automatically every minute

#### Time Range Selection
- **Available Ranges**: 1h, 6h, 24h, 7d, 30d
- **Default**: Last 24 hours
- **Custom**: User-defined time ranges
- **Real-time**: Live data updates

### Panel Interaction

#### Drill-Down Capabilities
- **Click to Expand**: Click panels for detailed views
- **Time Range Navigation**: Navigate to specific time periods
- **Service Filtering**: Filter data within panels

#### Data Export
- **CSV Export**: Download panel data for analysis
- **Image Export**: Save charts as images
- **JSON Export**: Export raw data for processing

### Dashboard Sharing

#### Sharing Options
- **View-Only Links**: Share dashboards with stakeholders
- **Embedded Views**: Integrate into other applications
- **Scheduled Reports**: Automated report generation

#### Access Control
- **Public Sharing**: Limited to organization members
- **Role-Based Access**: Different views for different roles
- **Audit Logging**: Track who accessed what and when

## Customer Onboarding

### Initial Setup Process

#### 1. Organization Creation
- **Grafana Organization**: Customer-specific organization setup
- **User Accounts**: Admin and user account creation
- **Permissions**: Role-based access configuration

#### 2. Dashboard Provisioning
- **Template Selection**: SLA tier-appropriate dashboard
- **Data Source Configuration**: Tenant-specific InfluxDB connection
- **Initial Data Population**: Historical data loading

#### 3. User Training
- **Dashboard Overview**: Key features and capabilities
- **Navigation Training**: How to use template variables
- **Alert Configuration**: Setting up performance alerts

### Configuration Steps

#### Dashboard Customization
- **SLA Thresholds**: Configure based on customer tier
- **Alert Rules**: Set up performance and SLA alerts
- **Refresh Intervals**: Configure update frequency

#### Data Source Setup
- **InfluxDB Connection**: Tenant-specific database connection
- **Token Configuration**: Secure access token setup
- **Query Templates**: Pre-configured tenant-isolated queries

### User Access Management

#### Admin Users
- **Full Access**: Dashboard configuration and user management
- **Alert Management**: Configure and manage alerts
- **Data Export**: Full data access and export capabilities

#### Standard Users
- **Dashboard Access**: View and interact with dashboards
- **Limited Configuration**: Basic dashboard customization
- **Data Export**: Limited export capabilities

#### Viewer Users
- **Read-Only Access**: View dashboards without modification
- **No Configuration**: Cannot change dashboard settings
- **Limited Export**: Basic data export only

## Troubleshooting

### Common Dashboard Issues

#### No Data Displayed
- **Check Time Range**: Ensure time range includes data
- **Verify Service Filter**: Check if service filter is too restrictive
- **Data Source Connection**: Verify InfluxDB connectivity
- **Tenant ID**: Confirm correct tenant_id filtering

#### Slow Dashboard Loading
- **Query Optimization**: Check for complex queries
- **Time Range**: Reduce time range for faster loading
- **Data Volume**: Large datasets may cause delays
- **Network Issues**: Check network connectivity

#### Missing Panels
- **Panel Configuration**: Verify panel settings
- **Data Availability**: Check if data exists for the time range
- **Permissions**: Ensure user has access to all panels
- **Template Variables**: Check variable configuration

### Data Connectivity Issues

#### InfluxDB Connection Problems
- **Network Connectivity**: Verify network access to InfluxDB
- **Authentication**: Check API token validity
- **Bucket Access**: Confirm bucket permissions
- **Service Status**: Verify InfluxDB service is running

#### Query Execution Errors
- **Syntax Errors**: Check Flux query syntax
- **Missing Fields**: Verify required fields exist in data
- **Time Range Issues**: Check time range validity
- **Resource Limits**: Monitor query timeout and memory limits

### Performance Issues

#### High Query Latency
- **Query Complexity**: Simplify complex queries
- **Time Range**: Reduce query time range
- **Aggregation**: Use appropriate aggregation functions
- **Indexing**: Check InfluxDB index configuration

#### Memory Usage
- **Query Optimization**: Optimize query memory usage
- **Data Volume**: Limit data processed in single queries
- **Caching**: Enable query result caching
- **Resource Limits**: Set appropriate memory limits

### Getting Help

#### Support Channels
- **Documentation**: Check this guide and related docs
- **Logs**: Review application and system logs
- **Monitoring**: Check system health metrics
- **Support Team**: Contact Bhashini support team

#### Escalation Process
1. **Self-Service**: Check documentation and logs
2. **Team Support**: Contact customer success team
3. **Technical Support**: Escalate to technical team
4. **Emergency**: Critical issues escalation process

## Customization and Extensions

### Available Customization Options

#### Dashboard Layout
- **Panel Arrangement**: Customize panel positions and sizes
- **Color Schemes**: Choose from available color themes
- **Refresh Intervals**: Configure update frequency
- **Time Ranges**: Set default time range preferences

#### Panel Configuration
- **Thresholds**: Adjust performance thresholds
- **Units**: Configure measurement units
- **Formats**: Customize number and date formats
- **Alerts**: Set up custom alert rules

#### Template Variables
- **Service Filters**: Customize available service options
- **Time Ranges**: Add custom time range options
- **Metric Types**: Configure available metric filters
- **Custom Variables**: Add organization-specific variables

### Requesting New Features

#### Feature Request Process
1. **Documentation**: Document the requested feature
2. **Business Case**: Explain business value and impact
3. **Technical Details**: Provide technical requirements
4. **Priority**: Indicate urgency and importance

#### Available Extensions
- **Custom Panels**: Add organization-specific metrics
- **External Integrations**: Connect to other monitoring systems
- **Custom Alerts**: Configure organization-specific alerting
- **Data Sources**: Add additional data sources

### Integration Options

#### External Systems
- **Ticketing Systems**: Integrate with support ticketing
- **Notification Systems**: Connect to Slack, Teams, or email
- **Monitoring Tools**: Integrate with existing monitoring
- **Analytics Platforms**: Export data to analytics tools

#### API Access
- **Grafana API**: Programmatic dashboard management
- **InfluxDB API**: Direct data access and querying
- **Custom Endpoints**: Organization-specific APIs
- **Webhook Integration**: Real-time event notifications

### Best Practices

#### Dashboard Design
- **Clarity**: Keep dashboards simple and focused
- **Consistency**: Use consistent naming and formatting
- **Performance**: Optimize queries for fast loading
- **Accessibility**: Ensure usability for all users

#### Data Management
- **Retention**: Follow data retention policies
- **Backup**: Regular backup of dashboard configurations
- **Versioning**: Track dashboard changes and versions
- **Documentation**: Document custom configurations

#### User Experience
- **Training**: Provide user training and documentation
- **Feedback**: Collect user feedback for improvements
- **Updates**: Regular dashboard updates and improvements
- **Support**: Provide ongoing user support

---

## Conclusion

This guide provides comprehensive information about using and managing customer dashboards in the Bhashini QoS monitoring system. By following these guidelines, customers can effectively monitor their service performance, track SLA compliance, and optimize their API usage.

For additional support or questions, please contact the Bhashini support team or refer to the technical documentation.

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Author**: Bhashini Development Team
