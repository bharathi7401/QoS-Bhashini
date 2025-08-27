#!/bin/bash

# Dashboard Formatting Validation Script
# This script enforces all formatting guidelines for Grafana dashboards

set -e  # Exit on any error

echo "🔍 Validating Dashboard Formatting Guidelines..."
echo "================================================"

ERROR_COUNT=0
DASHBOARD_COUNT=0

# Function to count errors
count_error() {
    echo "❌ ERROR: $1"
    ERROR_COUNT=$((ERROR_COUNT + 1))
}

# Function to check a dashboard file
validate_dashboard() {
    local file="$1"
    local dashboard_name=$(basename "$file" .json)
    
    echo "📊 Checking: $dashboard_name"
    DASHBOARD_COUNT=$((DASHBOARD_COUNT + 1))
    
    # Check 1: No raw data objects in titles or content
    if grep -q "_value.*{" "$file"; then
        count_error "Raw data objects found in $dashboard_name"
    fi
    
    # Check 2: No units in panel titles
    if grep -q "title.*[%ms]" "$file"; then
        count_error "Units found in panel titles in $dashboard_name"
    fi
    
    # Check 3: All panels have displayName in fieldConfig
    if grep -A 10 "fieldConfig.*defaults" "$file" | grep -q "defaults" && \
       ! grep -A 10 "fieldConfig.*defaults" "$file" | grep -q "displayName"; then
        count_error "Missing displayName in fieldConfig for $dashboard_name"
    fi
    
    # Check 4: Flux queries use map() function for clean output
    if grep -q "query.*from.*bucket" "$file" && \
       ! grep -q "map(fn:" "$file"; then
        count_error "Missing map() function in Flux queries for $dashboard_name"
    fi
    
    # Check 5: No technical field names exposed to users
    if grep -q "_measurement\|_field\|_value" "$file" | grep -v "filter"; then
        count_error "Technical field names exposed in $dashboard_name"
    fi
    
    # Check 6: Proper unit configuration
    if grep -q "unit.*requests_per_minute\|unit.*percent\|unit.*ms" "$file"; then
        echo "✅ Proper units configured in $dashboard_name"
    else
        count_error "Missing or incorrect unit configuration in $dashboard_name"
    fi
    
    # Check 7: Clean panel titles (no technical terms)
    if grep -q "title.*raw\|title.*object\|title.*data" "$file"; then
        count_error "Technical terms in panel titles for $dashboard_name"
    fi
    
    echo "✅ $dashboard_name validation completed"
    echo "---"
}

# Find all dashboard files
echo "🔍 Scanning for dashboard files..."
DASHBOARD_FILES=$(find grafana/provisioning/dashboards -name "*.json" -type f)

if [ -z "$DASHBOARD_FILES" ]; then
    echo "❌ No dashboard files found!"
    exit 1
fi

# Validate each dashboard
for file in $DASHBOARD_FILES; do
    validate_dashboard "$file"
done

# Summary
echo "================================================"
echo "📊 Validation Summary:"
echo "   Dashboards checked: $DASHBOARD_COUNT"
echo "   Errors found: $ERROR_COUNT"

if [ $ERROR_COUNT -eq 0 ]; then
    echo "🎉 All dashboards pass formatting validation!"
    echo "✅ Formatting guidelines are being followed correctly."
    exit 0
else
    echo "❌ $ERROR_COUNT formatting violations found!"
    echo "🔧 Please fix these issues before committing."
    echo ""
    echo "📋 Common fixes:"
    echo "   - Add map() functions to Flux queries"
    echo "   - Remove units from panel titles"
    echo "   - Add displayName to fieldConfig"
    echo "   - Use proper unit settings"
    echo "   - Clean up technical field names"
    exit 1
fi
