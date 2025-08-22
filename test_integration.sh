#!/bin/bash

# Integration Test Script for CrewAI Agent + MCP Service
# Tests the complete end-to-end workflow

set -e

echo "🚀 Starting CrewAI Agent + MCP Service Integration Test"
echo "======================================================"

# Function to check if a service is ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to become ready after $max_attempts attempts"
    return 1
}

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down > /dev/null 2>&1 || true

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose up -d --build

# Wait for all services to be ready
echo ""
echo "⏳ Waiting for services to become ready..."

wait_for_service "http://localhost:5432" "PostgreSQL" &
wait_for_service "http://localhost:8000/health" "MCP Service" &
wait_for_service "http://localhost:8001/health" "CrewAI Agent" &

# Wait for all background jobs to complete
wait

echo ""
echo "📊 Service Status Check:"
echo "======================="

# Check service status
echo -n "PostgreSQL: "
if docker-compose ps postgres | grep -q "Up"; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo -n "MCP Service: "
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Not healthy"
fi

echo -n "CrewAI Agent: "
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Not healthy"
fi

echo ""
echo "🧪 Running Integration Tests:"
echo "============================="

# Run the existing MCP service tests first
echo ""
echo "1️⃣  Testing MCP Service (existing functionality)..."
python3 test_mcp_tools.py

echo ""
echo "2️⃣  Testing CrewAI Agent Integration..."
python3 test_crewai_agent.py

echo ""
echo "🎉 Integration Test Complete!"
echo "=============================="

echo ""
echo "📋 All Services Running:"
echo "- PostgreSQL Database: http://localhost:5432"
echo "- MCP Service: http://localhost:8000"
echo "- CrewAI Agent: http://localhost:8001"
echo "- pgAdmin: http://localhost:8080"

echo ""
echo "🔗 Try the CrewAI Agent:"
echo 'curl -X POST http://localhost:8001/agent/execute \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"request": "Create a project called '\''Test Project'\'' and add a task '\''Setup environment'\''"}'\'

echo ""
echo "✅ Integration test completed successfully!"