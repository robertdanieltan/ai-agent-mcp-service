#!/usr/bin/env python3
"""
Python Test Script for MCP Task Management Service
Tests all 7 MCP tools via HTTP API with detailed validation
"""

import requests
import json
import sys
from datetime import datetime

class MCPTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.tools_url = f"{base_url}/tools/call"
        self.health_url = f"{base_url}/health"
        self.passed = 0
        self.failed = 0
        
    def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool"""
        if arguments is None:
            arguments = {}
        
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        try:
            response = requests.post(self.tools_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_health_check(self):
        """Test 1: Health Check"""
        print("1. Health Check... ", end="")
        try:
            response = requests.get(self.health_url, timeout=5)
            data = response.json()
            if response.status_code == 200 and data.get("status") == "healthy":
                print("✅ PASS")
                self.passed += 1
                return True
            else:
                print(f"❌ FAIL: {data}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_list_all_projects(self):
        """Test 2: List All Projects"""
        print("2. List All Projects... ", end="")
        result = self.call_tool("list_all_projects")
        
        if result.get("success") and "projects" in result:
            projects = result["projects"]
            print(f"✅ PASS")
            print(f"   Found {len(projects)} projects")
            for project in projects:
                print(f"   - {project['name']} (ID: {project['id']})")
            self.passed += 1
            return projects
        else:
            print(f"❌ FAIL: {result}")
            self.failed += 1
            return []
    
    def test_get_task_summary(self):
        """Test 3: Get Task Summary"""
        print("3. Get Task Summary... ", end="")
        result = self.call_tool("get_task_summary")
        
        if result.get("success") and "summary" in result:
            summary = result["summary"]
            print("✅ PASS")
            print(f"   Total tasks: {summary['total_tasks']}")
            print(f"   Pending: {summary['pending']}")
            print(f"   In Progress: {summary['in_progress']}")
            print(f"   Completed: {summary['completed']}")
            print(f"   Cancelled: {summary['cancelled']}")
            self.passed += 1
            return summary
        else:
            print(f"❌ FAIL: {result}")
            self.failed += 1
            return {}
    
    def test_get_tasks_by_status(self):
        """Test 4: Get Tasks by Status"""
        print("4. Get Tasks by Status... ", end="")
        
        # Test all statuses
        statuses = ["pending", "in_progress", "completed", "cancelled"]
        all_passed = True
        
        for status in statuses:
            result = self.call_tool("get_tasks_by_status", {"status": status})
            if not result.get("success"):
                print(f"❌ FAIL for {status}: {result}")
                all_passed = False
                break
        
        if all_passed:
            print("✅ PASS")
            print(f"   Successfully tested all status filters: {', '.join(statuses)}")
            self.passed += 1
        else:
            self.failed += 1
    
    def test_get_project_tasks(self, projects):
        """Test 5: Get Project Tasks"""
        print("5. Get Project Tasks... ", end="")
        
        if not projects:
            print("❌ SKIP: No projects available")
            return
        
        project_id = projects[0]["id"]
        result = self.call_tool("get_project_tasks", {"project_id": project_id})
        
        if result.get("success") and "tasks" in result:
            tasks = result["tasks"]
            print("✅ PASS")
            print(f"   Found {len(tasks)} tasks for project '{projects[0]['name']}'")
            for task in tasks[:3]:  # Show first 3 tasks
                print(f"   - {task['title']} ({task['status']})")
            if len(tasks) > 3:
                print(f"   ... and {len(tasks) - 3} more")
            self.passed += 1
        else:
            print(f"❌ FAIL: {result}")
            self.failed += 1
    
    def test_create_project(self):
        """Test 6: Create New Project"""
        print("6. Create New Project... ", end="")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_data = {
            "name": f"Python Test Project {timestamp}",
            "description": "A test project created by Python automated testing"
        }
        
        result = self.call_tool("create_project", project_data)
        
        if result.get("success") and "project" in result:
            project = result["project"]
            print("✅ PASS")
            print(f"   Created project '{project['name']}' with ID: {project['id']}")
            self.passed += 1
            return project
        else:
            print(f"❌ FAIL: {result}")
            self.failed += 1
            return None
    
    def test_create_task(self, project):
        """Test 7: Create New Task"""
        print("7. Create New Task... ", end="")
        
        if not project:
            print("❌ SKIP: No project available")
            return None
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        task_data = {
            "title": f"Python Test Task {timestamp}",
            "description": "A test task created by Python automated testing",
            "project_id": project["id"],
            "priority": "high",
            "assigned_to": "Python Tester"
        }
        
        result = self.call_tool("create_task", task_data)
        
        if result.get("success") and "task" in result:
            task = result["task"]
            print("✅ PASS")
            print(f"   Created task '{task['title']}' with ID: {task['id']}")
            print(f"   Priority: {task['priority']}, Assigned to: {task['assigned_to']}")
            self.passed += 1
            return task
        else:
            print(f"❌ FAIL: {result}")
            self.failed += 1
            return None
    
    def test_update_task_status(self, task):
        """Test 8: Update Task Status"""
        print("8. Update Task Status... ", end="")
        
        if not task:
            print("❌ SKIP: No task available")
            return
        
        # Test status progression: pending -> in_progress -> completed
        statuses = ["in_progress", "completed"]
        
        for status in statuses:
            result = self.call_tool("update_task_status", {
                "task_id": task["id"],
                "status": status
            })
            
            if not result.get("success"):
                print(f"❌ FAIL updating to {status}: {result}")
                self.failed += 1
                return
        
        print("✅ PASS")
        print(f"   Successfully updated task {task['id']} through status progression")
        self.passed += 1
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Testing MCP Task Management Service (Python)")
        print("=" * 50)
        print()
        
        # Test sequence
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return False
        
        projects = self.test_list_all_projects()
        summary = self.test_get_task_summary()
        self.test_get_tasks_by_status()
        self.test_get_project_tasks(projects)
        
        new_project = self.test_create_project()
        new_task = self.test_create_task(new_project)
        self.test_update_task_status(new_task)
        
        print()
        print("=" * 50)
        print(f"🎉 Test Results: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print("✅ All tests passed successfully!")
            
            # Show final summary
            print("\n📊 Final Task Summary:")
            final_summary = self.call_tool("get_task_summary")
            if final_summary.get("success"):
                summary = final_summary["summary"]
                print(json.dumps(summary, indent=2))
            
            return True
        else:
            print("❌ Some tests failed!")
            return False

def main():
    tester = MCPTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()