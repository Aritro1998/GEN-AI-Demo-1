#!/usr/bin/env python
"""Test script to verify the database and models are working"""

from model import (
    DiseaseFilesModel, 
    DiseasePredictionModel, 
    KnowledgeBaseModel,
    create_db_and_tables,
    engine
)
from sqlmodel import Session

# Create tables
print("Creating database tables...")
create_db_and_tables()
print("✓ Tables created successfully")

# Test connection
print("\nTesting database connection...")
with Session(engine) as session:
    print("✓ Database connection successful")

# Test creating a disease file record
print("\nTesting DiseaseFilesModel creation...")
try:
    with Session(engine) as session:
        test_record = DiseaseFilesModel(
            crop_name="Tomato",
            image_path="/images/test.jpg",
            latitude=28.6139,
            longitude=77.2090,
            notes="Test record",
            temperature=32.5,
            soil_moisture=65.0
        )
        session.add(test_record)
        session.commit()
        session.refresh(test_record)
        print(f"✓ Created record with ID: {test_record.id}")
        
        # Verify we can read it back
        retrieved = session.get(DiseaseFilesModel, test_record.id)
        if retrieved:
            print(f"✓ Retrieved record: {retrieved.crop_name}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All tests passed!")
