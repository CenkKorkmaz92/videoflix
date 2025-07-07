#!/usr/bin/env python3
"""
Quick API test runner to verify login endpoint functionality
Run this before importing the Postman collection to ensure everything works.
"""

import requests
import json
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_endpoint(method, url, data=None, headers=None):
    """Test an endpoint and return results."""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=10)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.json() if response.content else {},
            'success': True
        }
    except requests.exceptions.RequestException as e:
        return {
            'status_code': None,
            'error': str(e),
            'success': False
        }
    except json.JSONDecodeError:
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.text,
            'success': True
        }

def print_test_result(test_name, result):
    """Print formatted test result."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    if not result['success']:
        print(f"❌ FAILED: {result['error']}")
        return False
    
    status = result['status_code']
    print(f"Status Code: {status}")
    
    if 'Set-Cookie' in result['headers']:
        print(f"Cookies Set: {result['headers']['Set-Cookie'][:100]}...")
    
    if isinstance(result['data'], dict):
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    else:
        print(f"Response: {result['data'][:200]}...")
    
    return True

def main():
    """Run all login endpoint tests."""
    print("🚀 Videoflix Login Endpoint Test Runner")
    print(f"Testing: {API_BASE}/login/")
    
    tests = [
        {
            'name': 'Valid Login (200)',
            'method': 'POST',
            'data': {'email': 'test@example.com', 'password': 'TestPass123'},
            'expected_status': 200
        },
        {
            'name': 'Invalid Password (400)',
            'method': 'POST',
            'data': {'email': 'test@example.com', 'password': 'wrongpassword'},
            'expected_status': 400
        },
        {
            'name': 'Missing Email (400)',
            'method': 'POST',
            'data': {'password': 'TestPass123'},
            'expected_status': 400
        },
        {
            'name': 'Missing Password (400)',
            'method': 'POST',
            'data': {'email': 'test@example.com'},
            'expected_status': 400
        },
        {
            'name': 'GET Method Not Allowed (405)',
            'method': 'GET',
            'data': None,
            'expected_status': 405
        },
        {
            'name': 'Invalid JSON (400)',
            'method': 'POST',
            'data': None,
            'expected_status': 400,
            'raw_body': '{ invalid json'
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        url = f"{API_BASE}/login/"
        
        if 'raw_body' in test:
            # Special case for invalid JSON
            try:
                response = requests.post(
                    url, 
                    data=test['raw_body'], 
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                result = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response.text,
                    'success': True
                }
            except Exception as e:
                result = {'success': False, 'error': str(e)}
        else:
            result = test_endpoint(test['method'], url, test['data'])
        
        success = print_test_result(test['name'], result)
        
        if success and result['status_code'] == test['expected_status']:
            print(f"✅ PASSED: Expected status {test['expected_status']}")
            passed += 1
        elif success:
            print(f"⚠️ UNEXPECTED STATUS: Expected {test['expected_status']}, got {result['status_code']}")
        else:
            print(f"❌ FAILED: Could not complete test")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 All tests passed! Ready to import Postman collection.")
        return 0
    else:
        print("⚠️ Some tests failed. Check your server and database setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
