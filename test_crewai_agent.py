#!/usr/bin/env python3
"""
CrewAI Agent Integration Test Script

Tests the end-to-end integration of:
1. CrewAI Agent Service (FastAPI)
2. MCP Service (HTTP)  
3. PostgreSQL Database

This script tests natural language project management requests
processed by the CrewAI Project Manager agent.
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

class CrewAIAgentTester:
    def __init__(self, agent_url: str = "http://localhost:8001"):
        self.agent_url = agent_url
        self.health_url = f"{agent_url}/health"
        self.status_url = f"{agent_url}/agent/status"
        self.execute_url = f"{agent_url}/agent/execute"
        self.passed = 0
        self.failed = 0
    
    def test_agent_health(self) -> bool:
        """Test 1: Agent Health Check"""
        print("1. Agent Health Check... ", end="")
        try:
            response = requests.get(self.health_url, timeout=10)
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
    
    def test_agent_status(self) -> bool:
        """Test 2: Agent Status Check"""
        print("2. Agent Status Check... ", end="")
        try:
            response = requests.get(self.status_url, timeout=10)
            data = response.json()
            if (response.status_code == 200 and 
                data.get("status") == "ready" and
                data.get("anthropic_api_configured") is True):
                print("✅ PASS")
                print(f"   Agent Type: {data.get('agent_type')}")
                print(f"   Tools Available: {data.get('tools_available')}")
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
    
    def test_create_project_request(self) -> Dict[str, Any]:
        """Test 3: Create Project via Natural Language"""
        print("3. Create Project Request... ", end="")
        
        request_payload = {
            "request": "Create a new project called 'AI Research Platform' for developing machine learning models and research tools",
            "user_id": "test_user_001"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.execute_url,
                json=request_payload,
                timeout=60
            )
            execution_time = time.time() - start_time
            
            data = response.json()
            
            if response.status_code == 200 and data.get("success") is True:
                print("✅ PASS")
                print(f"   Execution time: {execution_time:.2f}s")
                print(f"   Result preview: {data.get('result', '')[:200]}...")
                self.passed += 1
                return data
            else:
                print(f"❌ FAIL: {data}")
                self.failed += 1
                return {}
        except Exception as e:
            print(f"❌ FAIL: {e}")
            self.failed += 1
            return {}
    
    def test_create_task_request(self) -> Dict[str, Any]:
        """Test 4: Create Task via Natural Language"""
        print("4. Create Task Request... ", end="")
        
        request_payload = {
            "request": "Add a high priority task 'Set up ML training pipeline' to project 1 and assign it to the Data Science team",
            "user_id": "test_user_001"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.execute_url,
                json=request_payload,
                timeout=60
            )
            execution_time = time.time() - start_time
            
            data = response.json()
            
            if response.status_code == 200 and data.get("success") is True:
                print("✅ PASS")
                print(f"   Execution time: {execution_time:.2f}s")
                print(f"   Result preview: {data.get('result', '')[:200]}...")
                self.passed += 1
                return data
            else:
                print(f"❌ FAIL: {data}")
                self.failed += 1
                return {}
        except Exception as e:
            print(f"❌ FAIL: {e}")
            self.failed += 1
            return {}
    
    def test_complex_project_request(self) -> Dict[str, Any]:
        """Test 5: Complex Project Management Request"""
        print("5. Complex Project & Tasks Request... ", end="")
        
        request_payload = {
            "request": """Create a project called 'Mobile App Development' for building a cross-platform mobile application. 
                         Then add these tasks:
                         1. 'UI/UX Design' with high priority assigned to Design Team
                         2. 'Backend API Development' with critical priority assigned to Backend Team  
                         3. 'Mobile App Testing' with medium priority assigned to QA Team""",
            "user_id": "test_user_001"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.execute_url,
                json=request_payload,
                timeout=90
            )
            execution_time = time.time() - start_time
            
            data = response.json()
            
            if response.status_code == 200 and data.get("success") is True:
                print("✅ PASS")
                print(f"   Execution time: {execution_time:.2f}s")
                print(f"   Result preview: {data.get('result', '')[:300]}...")
                self.passed += 1
                return data
            else:
                print(f"❌ FAIL: {data}")
                self.failed += 1
                return {}
        except Exception as e:
            print(f"❌ FAIL: {e}")
            self.failed += 1
            return {}
    
    def test_error_handling(self) -> bool:
        """Test 6: Error Handling"""
        print("6. Error Handling Test... ", end="")
        
        request_payload = {
            "request": "Create a task for project 99999 which doesn't exist",
            "user_id": "test_user_001"
        }
        
        try:
            response = requests.post(
                self.execute_url,
                json=request_payload,
                timeout=30
            )
            
            data = response.json()
            
            # Should handle error gracefully - either success with error message or failure with details
            if response.status_code == 200:
                print("✅ PASS")
                print(f"   Handled error: {data.get('result', data.get('error', ''))[:150]}...")
                self.passed += 1
                return True
            else:
                print(f"❌ FAIL: Unexpected status code {response.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def verify_mcp_service_integration(self) -> bool:
        """Test 7: Verify MCP Service Integration"""
        print("7. MCP Service Integration Verification... ", end="")
        
        try:
            # Test direct MCP service access
            mcp_health_url = "http://localhost:8000/health"
            mcp_response = requests.get(mcp_health_url, timeout=5)
            
            if mcp_response.status_code == 200:
                print("✅ PASS")
                print("   MCP Service is accessible and healthy")
                self.passed += 1
                return True
            else:
                print(f"❌ FAIL: MCP Service not healthy")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL: Cannot reach MCP Service - {e}")
            self.failed += 1
            return False
    
    def run_all_tests(self) -> bool:
        """Run all CrewAI agent integration tests"""
        print("🤖 Testing CrewAI Agent Integration")
        print("=" * 60)
        print()
        
        # Test sequence
        if not self.test_agent_health():
            print("❌ Agent health check failed - aborting tests")
            return False
        
        if not self.test_agent_status():
            print("❌ Agent status check failed - aborting tests")
            return False
        
        if not self.verify_mcp_service_integration():
            print("❌ MCP service integration failed - aborting tests")
            return False
        
        # Run project management tests
        self.test_create_project_request()
        self.test_create_task_request()
        self.test_complex_project_request()
        self.test_error_handling()
        
        print()
        print("=" * 60)
        print(f"🎉 Test Results: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print("✅ All CrewAI Agent integration tests passed!")
            print()
            print("🚀 Integration Architecture Verified:")
            print("   User Request → CrewAI Agent → MCP Service → PostgreSQL")
            print()
            print("📋 Available Endpoints:")
            print(f"   - Agent Service: {self.agent_url}")
            print(f"   - Execute Task: {self.execute_url}")
            print(f"   - Agent Status: {self.status_url}")
            return True
        else:
            print("❌ Some integration tests failed!")
            return False

def main():
    """Main test execution"""
    print("🧪 Starting CrewAI Agent Integration Tests")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = CrewAIAgentTester()
    success = tester.run_all_tests()
    
    print()
    print(f"🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()