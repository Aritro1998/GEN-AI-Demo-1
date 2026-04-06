#!/usr/bin/env python
"""Simple test to verify API works"""

try:
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    print("Testing API...")
    
    # Test create disease file
    payload = {
        "crop_name": "Tomato",
        "image_path": "/images/test.jpg",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "notes": "Test disease",
        "weather": "normal"
    }
    
    response = client.post("/api/disease-files/", json=payload)
    print(f"CREATE STATUS: {response.status_code}")
    
    if response.status_code == 201:
        print("SUCCESS: Disease file created!")
        data = response.json()
        print(f"Created ID: {data.get('id')}")
    else:
        print(f"ERROR: {response.text}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
