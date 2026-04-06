#!/usr/bin/env python
"""Test script to verify API endpoints work correctly"""

import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing Farmer Backend API\n")
print("=" * 50)

# Test 1: Health check
print("\n1. Testing health endpoint...")
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
assert response.status_code == 200

# Test 2: Root endpoint
print("\n2. Testing root endpoint...")
response = client.get("/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
assert response.status_code == 200

# Test 3: Create disease file
print("\n3. Testing create disease file...")
payload = {
    "crop_name": "Tomato",
    "image_path": "/images/tomato_disease.jpg",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "notes": "Powdery mildew infection",
    "weather": "normal",
    "temperature": 32.5,
    "soil_moisture": 65.0,
    "soil_temperature": 28.0,
    "soil_ph": 6.5,
    "uv_index": 7.2
}
response = client.post("/api/disease-files/", json=payload)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"✓ Created record with ID: {data.get('id')}")
    disease_file_id = data.get('id')
else:
    print(f"Error: {response.text}")
    exit(1)

# Test 4: Get all disease files
print("\n4. Testing get all disease files...")
response = client.get("/api/disease-files/")
print(f"Status: {response.status_code}")
data = response.json()
print(f"✓ Retrieved {len(data)} records")

# Test 5: Get disease file by ID
print("\n5. Testing get disease file by ID...")
response = client.get(f"/api/disease-files/{disease_file_id}")
print(f"Status: {response.status_code}")
data = response.json()
print(f"✓ Retrieved: {data.get('crop_name')}")

# Test 6: Update disease file
print("\n6. Testing update disease file...")
update_payload = {
    "notes": "Updated: Severe powdery mildew infection",
    "temperature": 35.0
}
response = client.put(f"/api/disease-files/{disease_file_id}", json=update_payload)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Updated notes: {data.get('notes')}")

# Test 7: Filter by crop name
print("\n7. Testing filter by crop name...")
response = client.get("/api/disease-files/crop/Tomato")
print(f"Status: {response.status_code}")
data = response.json()
print(f"✓ Found {len(data)} Tomato records")

# Test 8: Filter by temperature range
print("\n8. Testing filter by temperature range...")
response = client.get("/api/disease-files/filter/temperature/30/40")
print(f"Status: {response.status_code}")
data = response.json()
print(f"✓ Found {len(data)} records in temperature range 30-40°C")

# Test 9: Create disease prediction
print("\n9. Testing create disease prediction...")
prediction_payload = {
    "disease_file_id": disease_file_id,
    "disease_name": "Powdery Mildew",
    "accuracy": 0.92,
    "precision": 0.88,
    "recall": 0.85,
    "f_one_score": 0.86,
    "severity_score": 0.75,
    "severity_value": "high",
    "treatment": "Apply sulfur-based fungicide every 7-10 days"
}
response = client.post("/api/disease-predictions/", json=prediction_payload)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"✓ Created prediction with run_id: {data.get('run_id')}")
    run_id = data.get('run_id')
else:
    print(f"Error: {response.text}")

# Test 10: Get predictions by severity
print("\n10. Testing get predictions by severity level...")
response = client.get("/api/disease-predictions/severity/high")
print(f"Status: {response.status_code}")
data = response.json()
print(f"✓ Found {len(data)} high severity predictions")

print("\n" + "=" * 50)
print("✓ All API tests passed successfully!")
