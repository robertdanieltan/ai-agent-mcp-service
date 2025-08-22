#!/bin/bash

# Test script for MCP Task Management Service
# Tests all 7 MCP tools via HTTP API

MCP_URL="http://localhost:8000/tools/call"
HEADER="Content-Type: application/json"

echo "🧪 Testing MCP Task Management Service"
echo "======================================"

# Test 1: Health Check
echo -n "1. Health Check... "
health_response=$(curl -s http://localhost:8000/health)
if [[ $health_response == *"healthy"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL: $health_response"
    exit 1
fi

# Test 2: List All Projects
echo -n "2. List All Projects... "
projects_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "list_all_projects", "arguments": {}}')
if [[ $projects_response == *"success\":true"* && $projects_response == *"AI Development Project"* ]]; then
    echo "✅ PASS"
    project_count=$(echo $projects_response | grep -o '"id":[0-9]*' | wc -l)
    echo "   Found $project_count projects"
else
    echo "❌ FAIL: $projects_response"
fi

# Test 3: Get Task Summary
echo -n "3. Get Task Summary... "
summary_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "get_task_summary", "arguments": {}}')
if [[ $summary_response == *"success\":true"* && $summary_response == *"total_tasks"* ]]; then
    echo "✅ PASS"
    total_tasks=$(echo $summary_response | grep -o '"total_tasks":[0-9]*' | cut -d':' -f2)
    echo "   Total tasks: $total_tasks"
else
    echo "❌ FAIL: $summary_response"
fi

# Test 4: Get Tasks by Status (pending)
echo -n "4. Get Tasks by Status (pending)... "
pending_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "get_tasks_by_status", "arguments": {"status": "pending"}}')
if [[ $pending_response == *"success\":true"* ]]; then
    echo "✅ PASS"
    pending_count=$(echo $pending_response | grep -o '"id":[0-9]*' | wc -l)
    echo "   Found $pending_count pending tasks"
else
    echo "❌ FAIL: $pending_response"
fi

# Test 5: Get Project Tasks (project_id = 1)
echo -n "5. Get Project Tasks (project 1)... "
project_tasks_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "get_project_tasks", "arguments": {"project_id": 1}}')
if [[ $project_tasks_response == *"success\":true"* && $project_tasks_response == *"project_id\":1"* ]]; then
    echo "✅ PASS"
    task_count=$(echo $project_tasks_response | grep -o '"id":[0-9]*' | wc -l)
    echo "   Found $task_count tasks for project 1"
else
    echo "❌ FAIL: $project_tasks_response"
fi

# Test 6: Create New Project
echo -n "6. Create New Project... "
new_project_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "create_project", "arguments": {"name": "Test Project", "description": "A test project created by automated testing"}}')
if [[ $new_project_response == *"success\":true"* && $new_project_response == *"Test Project"* ]]; then
    echo "✅ PASS"
    new_project_id=$(echo $new_project_response | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "   Created project with ID: $new_project_id"
else
    echo "❌ FAIL: $new_project_response"
fi

# Test 7: Create New Task
echo -n "7. Create New Task... "
new_task_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "create_task", "arguments": {"title": "Test Task", "description": "A test task", "project_id": 1, "priority": "high", "assigned_to": "Test User"}}')
if [[ $new_task_response == *"success\":true"* && $new_task_response == *"Test Task"* ]]; then
    echo "✅ PASS"
    new_task_id=$(echo $new_task_response | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "   Created task with ID: $new_task_id"
    
    # Test 8: Update Task Status
    echo -n "8. Update Task Status... "
    update_response=$(curl -s -X POST $MCP_URL -H "$HEADER" -d "{\"name\": \"update_task_status\", \"arguments\": {\"task_id\": $new_task_id, \"status\": \"in_progress\"}}")
    if [[ $update_response == *"success\":true"* && $update_response == *"in_progress"* ]]; then
        echo "✅ PASS"
        echo "   Updated task $new_task_id to 'in_progress'"
    else
        echo "❌ FAIL: $update_response"
    fi
else
    echo "❌ FAIL: $new_task_response"
fi

echo ""
echo "🎉 All MCP tools tested successfully!"
echo ""
echo "📊 Final Summary:"
curl -s -X POST $MCP_URL -H "$HEADER" -d '{"name": "get_task_summary", "arguments": {}}' | python3 -m json.tool