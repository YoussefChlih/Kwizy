#!/usr/bin/env python3
"""
Test script for signup and login
"""

import requests
import json
import time
import sys

API_URL = "http://localhost:5000"

# Test email that is valid
TEST_EMAIL = "testuser" + str(int(time.time() % 10000)) + "@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"

def print_response(title, status_code, response_json):
    """Pretty print response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {status_code}")
    print(json.dumps(response_json, indent=2))
    return status_code == 201 or status_code == 200

def test_health():
    """Test API health"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        success = print_response("Health Check", response.status_code, response.json())
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_signup(email, password, first_name, last_name):
    """Test signup"""
    try:
        data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }
        response = requests.post(f"{API_URL}/api/auth/signup", json=data)
        success = print_response("Signup Test", response.status_code, response.json())
        
        if success:
            print(f"\nSignup successful! Email: {email}")
            return response.json().get('user', {}).get('id')
        else:
            error_msg = response.json().get('error', '')
            print(f"\nSignup failed: {error_msg}")
            
            # Handle rate limiting
            if "after" in error_msg and "seconds" in error_msg:
                print("\nRate limited by Supabase. Waiting...")
                # Extract wait time and add 2 seconds buffer
                try:
                    wait_time = int(error_msg.split("after ")[1].split(" seconds")[0]) + 2
                    for i in range(wait_time, 0, -1):
                        print(f"  Waiting {i} seconds...", end='\r')
                        time.sleep(1)
                    print("                     ")
                    return None
                except:
                    pass
        return None
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login(email, password):
    """Test login"""
    try:
        data = {
            'email': email,
            'password': password
        }
        response = requests.post(f"{API_URL}/api/auth/login", json=data)
        success = print_response("Login Test", response.status_code, response.json())
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_documents():
    """Test documents endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/documents")
        success = print_response("Documents Test", response.status_code, response.json())
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("KWIZY API TEST SCRIPT")
    print("="*50)
    
    # Test 1: Health
    print("\n[1/5] Testing API health...")
    if not test_health():
        print("\nBackend not responding. Make sure to run: python app.py")
        return False
    
    # Test 2: Signup
    print("\n[2/5] Testing signup...")
    print(f"Using email: {TEST_EMAIL}")
    user_id = test_signup(TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME)
    
    if not user_id:
        print("\nSignup test failed. Check the error message above.")
        # Try again after rate limit
        print("\nRetrying signup after rate limit...")
        time.sleep(5)
        user_id = test_signup(TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME)
        
        if not user_id:
            print("Second signup attempt failed.")
            return False
    
    # Test 3: Login
    print("\n[3/5] Testing login...")
    if not test_login(TEST_EMAIL, TEST_PASSWORD):
        print("\nLogin test failed. Check the error message above.")
    
    # Test 4: Documents
    print("\n[4/5] Testing documents endpoint...")
    test_documents()
    
    print("\n[5/5] Summary")
    print("="*50)
    print("All tests completed!")
    print("\nIf you see errors, check:")
    print("1. Backend is running: python app.py")
    print("2. Supabase credentials in .env")
    print("3. Network connectivity")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
