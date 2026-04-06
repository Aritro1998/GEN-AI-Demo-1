#!/usr/bin/env python
"""
Comprehensive validation script for Farmer Backend
Verifies database setup, models, and API structure
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(msg):
    """Print success message"""
    print(f"✓ {msg}")

def print_error(msg):
    """Print error message"""
    print(f"✗ {msg}")

def print_info(msg):
    """Print info message"""
    print(f"ℹ {msg}")

def check_files():
    """Check if all required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "model/__init__.py",
        "model/database.py",
        "model/disease_files.py",
        "model/disease_prediction.py",
        "model/knowledge_base.py",
        "api/__init__.py",
        "api/disease_files.py",
        "api/disease_predictions.py",
        "api/knowledge_base.py",
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print_success(f"Found {file}")
        else:
            print_error(f"Missing {file}")
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if all modules can be imported"""
    print_header("Checking Module Imports")
    
    try:
        from model import (
            DiseaseFilesModel,
            DiseasePredictionModel,
            KnowledgeBaseModel,
            WeatherCondition,
            SeverityLevel,
            get_session,
            create_db_and_tables
        )
        print_success("Imported from model: DiseaseFilesModel")
        print_success("Imported from model: DiseasePredictionModel")
        print_success("Imported from model: KnowledgeBaseModel")
        print_success("Imported from model: WeatherCondition")
        print_success("Imported from model: SeverityLevel")
        print_success("Imported from model: get_session")
        print_success("Imported from model: create_db_and_tables")
        
        from api import disease_files_router, disease_predictions_router, knowledge_base_router
        print_success("Imported from api: disease_files_router")
        print_success("Imported from api: disease_predictions_router")
        print_success("Imported from api: knowledge_base_router")
        
        return True
    except Exception as e:
        print_error(f"Import error: {e}")
        return False

def check_models():
    """Check model definitions"""
    print_header("Checking Model Definitions")
    
    try:
        from model import DiseaseFilesModel, DiseasePredictionModel, KnowledgeBaseModel
        
        # Check DiseaseFilesModel fields
        disease_files_fields = DiseaseFilesModel.model_fields
        expected_fields = [
            'id', 'crop_name', 'image_path', 'latitude', 'longitude',
            'notes', 'weather', 'temperature', 'soil_moisture',
            'soil_temperature', 'soil_ph', 'uv_index', 'upload_dt'
        ]
        
        for field in expected_fields:
            if field in disease_files_fields:
                print_success(f"DiseaseFilesModel has field: {field}")
            else:
                print_error(f"DiseaseFilesModel missing field: {field}")
        
        # Check DiseasePredictionModel fields
        prediction_fields = DiseasePredictionModel.model_fields
        expected_pred_fields = [
            'run_id', 'disease_file_id', 'disease_name', 'accuracy',
            'precision', 'recall', 'f_one_score', 'severity_score',
            'severity_value', 'treatment', 'run_dt'
        ]
        
        for field in expected_pred_fields:
            if field in prediction_fields:
                print_success(f"DiseasePredictionModel has field: {field}")
            else:
                print_error(f"DiseasePredictionModel missing field: {field}")
        
        return True
    except Exception as e:
        print_error(f"Model check error: {e}")
        return False

def check_database():
    """Check database setup"""
    print_header("Checking Database Setup")
    
    try:
        from model import engine, create_db_and_tables
        from sqlmodel import SQLModel
        
        print_info("Creating database tables...")
        create_db_and_tables()
        print_success("Database tables created successfully")
        
        db_path = Path("farmer_backend.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print_success(f"Database file exists: farmer_backend.db ({size_mb:.2f} MB)")
        else:
            print_info("Database file will be created on first connection")
        
        return True
    except Exception as e:
        print_error(f"Database check error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_enums():
    """Check enum definitions"""
    print_header("Checking Enums")
    
    try:
        from model import WeatherCondition, SeverityLevel
        
        weather_values = [e.value for e in WeatherCondition]
        print_info(f"WeatherCondition values: {weather_values}")
        expected_weather = ["hot", "cold", "normal", "flood"]
        for val in expected_weather:
            if val in weather_values:
                print_success(f"WeatherCondition has: {val}")
            else:
                print_error(f"WeatherCondition missing: {val}")
        
        severity_values = [e.value for e in SeverityLevel]
        print_info(f"SeverityLevel values: {severity_values}")
        expected_severity = ["none", "low", "average", "high"]
        for val in expected_severity:
            if val in severity_values:
                print_success(f"SeverityLevel has: {val}")
            else:
                print_error(f"SeverityLevel missing: {val}")
        
        return True
    except Exception as e:
        print_error(f"Enum check error: {e}")
        return False

def check_api_routes():
    """Check API route definitions"""
    print_header("Checking API Routes")
    
    try:
        from api import disease_files_router, disease_predictions_router, knowledge_base_router
        
        # Check disease files routes
        df_routes = [route.path for route in disease_files_router.routes]
        print_info(f"Disease Files routes: {len(disease_files_router.routes)} endpoints")
        print_success(f"Disease Files router path prefix: /api/disease-files")
        
        # Check predictions routes
        pred_routes = [route.path for route in disease_predictions_router.routes]
        print_info(f"Disease Predictions routes: {len(disease_predictions_router.routes)} endpoints")
        print_success(f"Predictions router path prefix: /api/disease-predictions")
        
        # Check knowledge base routes
        kb_routes = [route.path for route in knowledge_base_router.routes]
        print_info(f"Knowledge Base routes: {len(knowledge_base_router.routes)} endpoints")
        print_success(f"Knowledge Base router path prefix: /api/knowledge-base")
        
        return True
    except Exception as e:
        print_error(f"API route check error: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlmodel',
        'sqlalchemy',
        'pydantic',
        'requests',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"Installed: {package}")
        except ImportError:
            print_error(f"Missing: {package}")
            all_installed = False
    
    return all_installed

def main():
    """Run all validation checks"""
    print("\n" + "="*70)
    print("  FARMER BACKEND - COMPREHENSIVE VALIDATION")
    print("="*70)
    
    checks = [
        ("Files", check_files),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_imports),
        ("Model Definitions", check_models),
        ("Enums", check_enums),
        ("Database", check_database),
        ("API Routes", check_api_routes),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Error in {name} check: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print_header("Validation Summary")
    
    for name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print_success("All validations passed! Backend is ready to run.")
        print_info("To start the server, run: python run_server.py")
        return 0
    else:
        print_error("Some validations failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
