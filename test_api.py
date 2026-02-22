"""
Test script for Skill-Link API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_apis():
    print("=" * 50)
    print("Skill-Link API Test")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: Platform Info
    print("\n2. Testing Platform Info...")
    response = requests.get(f"{BASE_URL}/api/info")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 3: HR Register
    print("\n3. Testing HR Register...")
    hr_data = {
        "company_name": "Test Corp",
        "hr_name": "Test HR",
        "email": "testhr@test.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/hr/register", json=hr_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        hr_token = response.json().get('access_token')
        print(f"   Success! Token received")
    else:
        print(f"   Response: {response.json()}")
        hr_token = None
    
    # Test 4: HR Login
    print("\n4. Testing HR Login...")
    login_data = {
        "email": "testhr@test.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/hr/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        hr_token = response.json().get('access_token')
        print(f"   Success! Login successful")
    else:
        print(f"   Response: {response.json()}")
    
    # Test 5: Student Register
    print("\n5. Testing Student Register...")
    student_data = {
        "name": "Test Student",
        "email": "teststudent@test.com",
        "password": "test123",
        "branch": "Computer Science",
        "grad_year": 2025
    }
    response = requests.post(f"{BASE_URL}/api/students/register", json=student_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        student_token = response.json().get('access_token')
        print(f"   Success! Student registered")
    else:
        print(f"   Response: {response.json()}")
    
    # Test 6: Student Login
    print("\n6. Testing Student Login...")
    login_data = {
        "email": "teststudent@test.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/students/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        student_token = response.json().get('access_token')
        print(f"   Success! Student logged in")
    else:
        print(f"   Response: {response.json()}")
    
    print("\n" + "=" * 50)
    print("API Tests Complete!")
    print("=" * 50)
    print("\nPlatform: Skill-Link")
    print("Chatbot: CareerBot")
    print("Team: Team Arena")

if __name__ == "__main__":
    test_apis()
