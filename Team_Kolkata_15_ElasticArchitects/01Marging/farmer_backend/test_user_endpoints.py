#!/usr/bin/env python
"""
Test script to verify user creation endpoint works
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_create_user():
    """Test user creation endpoint"""
    print("\n" + "="*60)
    print("Testing User Creation Endpoint")
    print("="*60 + "\n")
    
    user_data = {
        "username": "testfarmer",
        "password": "TestPassword123!",
        "firstname": "Test",
        "lastname": "Farmer",
        "created_by": "admin",
        "user_role": "farmer",
        "location": "Farm Location",
        "phone": "1234567890"
    }
    
    try:
        print("Creating user with data:")
        print(json.dumps(user_data, indent=2))
        print()
        
        response = requests.post(f"{BASE_URL}/create", json=user_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ User creation successful!")
            return True
        else:
            print("\n❌ User creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login():
    """Test login endpoint"""
    print("\n" + "="*60)
    print("Testing Login Endpoint")
    print("="*60 + "\n")
    
    login_data = {
        "username": "testfarmer",
        "password": "TestPassword123!"
    }
    
    try:
        print("Logging in with credentials:")
        print(json.dumps(login_data, indent=2))
        print()
        
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200 and "x-access-token" in response.headers:
            print("\n✅ Login successful!")
            return response.headers.get("x-access-token")
        else:
            print("\n❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_current_user(token):
    """Test get current user endpoint"""
    print("\n" + "="*60)
    print("Testing Get Current User Endpoint")
    print("="*60 + "\n")
    
    try:
        print(f"Using token: {token[:20]}...")
        print()
        
        headers = {"x-access-token": token}
        response = requests.get(f"{BASE_URL}/current_user", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Get current user successful!")
            return True
        else:
            print("\n❌ Get current user failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("USER MANAGEMENT ENDPOINT TESTS")
    print("="*60)
    print("\nNote: Server must be running at http://localhost:8000")
    print("Start with: python run_server.py")
    
    # Wait a bit for server to be ready
    sleep(1)
    
    # Test create user
    if test_create_user():
        # Test login
        token = test_login()
        
        # Test get current user if we got a token
        if token:
            test_get_current_user(token)
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
