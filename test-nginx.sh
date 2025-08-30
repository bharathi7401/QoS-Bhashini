#!/bin/bash

echo "🚀 Testing Nginx startup..."

# Copy nginx config
cp /app/nginx.conf /etc/nginx/nginx.conf

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
echo "Testing nginx configuration..."
nginx -t

# Start nginx in foreground
echo "Starting nginx on 0.0.0.0:80..."
exec nginx -g "daemon off;"
