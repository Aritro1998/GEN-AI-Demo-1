"""
Comprehensive test script for Farmer Backend API
Tests all endpoints with real data
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_test(name):
    print(f"\n{BLUE}{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}{RESET}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

# Store IDs for relationship testing
created_disease_file_id = None
created_prediction_id = None
created_kb_id = None

def test_health_check():
    """Test if API is running"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"API is running: {response.json()}")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        return False

def test_create_disease_file():
    """Test creating a disease file"""
    global created_disease_file_id
    print_test("Create Disease File")
    
    payload = {
        "crop_name": "Tomato",
        "image_path": "/images/tomato_disease_001.jpg",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "notes": "Early blight symptoms observed on lower leaves",
        "weather": "hot",
        "temperature": 35.5,
        "soil_moisture": 65.0,
        "soil_temperature": 28.3,
        "soil_ph": 6.5,
        "uv_index": 8.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/disease-files/", json=payload)
        if response.status_code == 201:
            data = response.json()
            created_disease_file_id = data.get("id")
            print_success(f"Disease file created with ID: {created_disease_file_id}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_get_all_disease_files():
    """Test getting all disease files"""
    print_test("Get All Disease Files")
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-files/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} disease files")
            if data:
                print_info(f"First record: {json.dumps(data[0], indent=2)}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_get_disease_file_by_id():
    """Test getting a specific disease file"""
    print_test("Get Disease File by ID")
    
    if not created_disease_file_id:
        print_error("No disease file ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-files/{created_disease_file_id}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved disease file: {data.get('crop_name')}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_update_disease_file():
    """Test updating a disease file"""
    print_test("Update Disease File")
    
    if not created_disease_file_id:
        print_error("No disease file ID available")
        return False
    
    payload = {
        "notes": "Updated: Early blight confirmed, recommended fungicide treatment"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/disease-files/{created_disease_file_id}", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Disease file updated successfully")
            print_info(f"Updated notes: {data.get('notes')}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_filter_by_crop():
    """Test filtering disease files by crop"""
    print_test("Filter Disease Files by Crop")
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-files/filter-by-crop?crop_name=Tomato")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} tomato records")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_create_disease_prediction():
    """Test creating a disease prediction"""
    global created_prediction_id
    print_test("Create Disease Prediction")
    
    if not created_disease_file_id:
        print_error("No disease file ID available")
        return False
    
    payload = {
        "disease_file_id": created_disease_file_id,
        "disease_name": "Early Blight",
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.88,
        "f_one_score": 0.885,
        "severity_score": 0.75,
        "severity_value": "high",
        "treatment": "Apply Mancozeb or Chlorothalonil fungicide every 7-10 days"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/disease-predictions/", json=payload)
        if response.status_code == 201:
            data = response.json()
            created_prediction_id = data.get("id")
            print_success(f"Disease prediction created with ID: {created_prediction_id}")
            print_info(f"Disease: {data.get('disease_name')}, Accuracy: {data.get('accuracy')}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_get_all_predictions():
    """Test getting all disease predictions"""
    print_test("Get All Disease Predictions")
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-predictions/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} disease predictions")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_filter_predictions_by_disease():
    """Test filtering predictions by disease name"""
    print_test("Filter Predictions by Disease Name")
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-predictions/filter-by-disease?disease_name=Early%20Blight")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} Early Blight predictions")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_filter_predictions_by_severity():
    """Test filtering predictions by severity"""
    print_test("Filter Predictions by Severity Level")
    
    try:
        response = requests.get(f"{BASE_URL}/api/disease-predictions/filter-by-severity?severity_level=high")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} high-severity predictions")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_create_knowledge_base():
    """Test creating knowledge base entry"""
    global created_kb_id
    print_test("Create Knowledge Base Entry")
    
    payload = {
        "crop_name": "Potato",
        "disease_name": "Late Blight",
        "description": "Late blight is a destructive disease of potato and tomato",
        "symptoms": "Water-soaked spots on leaves, white mold on leaf undersides",
        "optimal_temperature": 18.0,
        "optimal_humidity": 85.0,
        "recommended_treatment": "Mancozeb or Metalaxyl fungicides",
        "prevention_methods": "Resistant varieties, crop rotation, remove infected plants",
        "disease_file_id": created_disease_file_id,
        "severity_score": 0.85,
        "severity_value": "high"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/knowledge-base/", json=payload)
        if response.status_code == 201:
            data = response.json()
            created_kb_id = data.get("kb_id")
            print_success(f"Knowledge base entry created with ID: {created_kb_id}")
            print_info(f"Disease: {data.get('disease_name')}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_get_knowledge_base():
    """Test getting knowledge base entries"""
    print_test("Get Knowledge Base Entries")
    
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge-base/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} knowledge base entries")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_delete_disease_file():
    """Test deleting a disease file"""
    print_test("Delete Disease File")
    
    if not created_disease_file_id:
        print_error("No disease file ID available")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/api/disease-files/{created_disease_file_id}")
        if response.status_code == 200:
            print_success("Disease file deleted successfully")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("FARMER BACKEND API - COMPREHENSIVE TEST SUITE")
    print(f"{'='*60}{RESET}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Create Disease File", test_create_disease_file),
        ("Get All Disease Files", test_get_all_disease_files),
        ("Get Disease File by ID", test_get_disease_file_by_id),
        ("Update Disease File", test_update_disease_file),
        ("Filter Disease Files by Crop", test_filter_by_crop),
        ("Create Disease Prediction", test_create_disease_prediction),
        ("Get All Predictions", test_get_all_predictions),
        ("Filter Predictions by Disease", test_filter_predictions_by_disease),
        ("Filter Predictions by Severity", test_filter_predictions_by_severity),
        ("Create Knowledge Base Entry", test_create_knowledge_base),
        ("Get Knowledge Base", test_get_knowledge_base),
        ("Delete Disease File", test_delete_disease_file),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Exception in {test_name}: {e}")
            failed += 1
    
    print(f"\n{BLUE}{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}{RESET}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"Total:  {passed + failed}\n")

if __name__ == "__main__":
    main()
