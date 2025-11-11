#!/usr/bin/env python3
"""
Test script for the Dog Management API Server
Run this after starting the Flask server to test all endpoints.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://127.0.0.1:5000"

def print_response(response, operation):
    """Print formatted response information."""
    print(f"\n{'='*50}")
    print(f"Operation: {operation}")
    print(f"Status Code: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    print('='*50)

def test_api():
    """Test all API endpoints."""
    
    print("🐕 Dog Management API Test Suite")
    print(f"Testing API at: {BASE_URL}")
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response, "GET /api/health")
    
    # Test 2: Get Stats (should be empty initially)
    print("\n2. Testing Stats...")
    response = requests.get(f"{BASE_URL}/api/stats")
    print_response(response, "GET /api/stats")
    
    # Test 3: Create Dog Record (POST)
    print("\n3. Creating Dog Record...")
    dog_data = {
        "userId": "testuser123",
        "name": "Buddy",
        "age": 3,
        "breeds": ["golden_retriever", "mixed"],
        "otherBreeds": "Some Labrador mix",
        "weight": 65.5
    }
    response = requests.post(f"{BASE_URL}/api/dogs", json=dog_data)
    print_response(response, "POST /api/dogs")
    
    # Test 4: Create Diet Record (POST)
    print("\n4. Creating Diet Record...")
    diet_data = {
        "userId": "testuser123",
        "foodType": "both",
        "brand": "Blue Buffalo",
        "amount": "2 cups dry, 1 can wet",
        "feedingTimes": 2
    }
    response = requests.post(f"{BASE_URL}/api/diets", json=diet_data)
    print_response(response, "POST /api/diets")
    
    # Test 5: Get All Dogs (GET)
    print("\n5. Getting All Dogs...")
    response = requests.get(f"{BASE_URL}/api/dogs")
    print_response(response, "GET /api/dogs")
    
    # Test 6: Get All Diets (GET)
    print("\n6. Getting All Diets...")
    response = requests.get(f"{BASE_URL}/api/diets")
    print_response(response, "GET /api/diets")
    
    # Test 7: Get Dog by User ID (GET)
    print("\n7. Getting Dog by User ID...")
    response = requests.get(f"{BASE_URL}/api/dogs/testuser123")
    print_response(response, "GET /api/dogs/testuser123")
    
    # Test 8: Get Diet by User ID (GET)
    print("\n8. Getting Diet by User ID...")
    response = requests.get(f"{BASE_URL}/api/diets/testuser123")
    print_response(response, "GET /api/diets/testuser123")
    
    # Test 9: Get User Records (GET)
    print("\n9. Getting User Records...")
    response = requests.get(f"{BASE_URL}/api/users/testuser123")
    print_response(response, "GET /api/users/testuser123")
    
    # Test 10: Update Dog Record (PUT)
    print("\n10. Updating Dog Record...")
    updated_dog_data = {
        "userId": "testuser123",
        "name": "Buddy Updated",
        "age": 4,
        "breeds": ["golden_retriever", "labrador_retriever"],
        "otherBreeds": "Golden Lab mix",
        "weight": 70.0
    }
    response = requests.put(f"{BASE_URL}/api/dogs/testuser123", json=updated_dog_data)
    print_response(response, "PUT /api/dogs/testuser123")
    
    # Test 11: Update Diet Record (PUT)
    print("\n11. Updating Diet Record...")
    updated_diet_data = {
        "userId": "testuser123",
        "foodType": "dry",
        "brand": "Purina Pro Plan",
        "amount": "3 cups",
        "feedingTimes": 3
    }
    response = requests.put(f"{BASE_URL}/api/diets/testuser123", json=updated_diet_data)
    print_response(response, "PUT /api/diets/testuser123")
    
    # Test 12: Get Stats After Updates
    print("\n12. Getting Updated Stats...")
    response = requests.get(f"{BASE_URL}/api/stats")
    print_response(response, "GET /api/stats")
    
    # Test 13: Test Error Cases
    print("\n13. Testing Error Cases...")
    
    # Try to create duplicate dog record
    response = requests.post(f"{BASE_URL}/api/dogs", json=dog_data)
    print_response(response, "POST /api/dogs (duplicate - should fail)")
    
    # Try to get non-existent user
    response = requests.get(f"{BASE_URL}/api/users/nonexistent")
    print_response(response, "GET /api/users/nonexistent (should fail)")
    
    # Try to update with invalid data
    invalid_dog_data = {
        "userId": "testuser123",
        "name": "",  # Empty name should fail
        "age": 35,   # Age too high
        "breeds": [],  # Empty breeds should fail
        "weight": -5   # Negative weight should fail
    }
    response = requests.put(f"{BASE_URL}/api/dogs/testuser123", json=invalid_dog_data)
    print_response(response, "PUT /api/dogs/testuser123 (invalid data - should fail)")
    
    # Test 14: Delete Diet Record (DELETE)
    print("\n14. Deleting Diet Record...")
    response = requests.delete(f"{BASE_URL}/api/diets/testuser123")
    print_response(response, "DELETE /api/diets/testuser123")
    
    # Test 15: Delete Dog Record (DELETE)
    print("\n15. Deleting Dog Record...")
    response = requests.delete(f"{BASE_URL}/api/dogs/testuser123")
    print_response(response, "DELETE /api/dogs/testuser123")
    
    # Test 16: Final Stats Check
    print("\n16. Final Stats Check...")
    response = requests.get(f"{BASE_URL}/api/stats")
    print_response(response, "GET /api/stats (after deletions)")
    
    print(f"\n{'='*60}")
    print("🎉 Test Suite Completed!")
    print("Check the results above to verify all operations worked correctly.")
    print(f"{'='*60}")

def test_connection():
    """Test if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    print("🔍 Checking if API server is running...")
    
    if not test_connection():
        print("❌ Error: Cannot connect to API server!")
        print("Make sure to start the Flask server first:")
        print("  python app.py")
        exit(1)
    
    print("✅ API server is running!")
    time.sleep(1)
    
    try:
        test_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")