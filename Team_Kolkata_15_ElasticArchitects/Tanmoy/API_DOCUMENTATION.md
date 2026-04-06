# Farmer Backend API - Complete Documentation

## Overview
The Farmer Backend API is a FastAPI-based REST API for managing crop diseases, predictions, and environmental data. It provides comprehensive endpoints for disease file management, disease predictions, and knowledge base operations.

## Features
- ✅ Complete CRUD operations for disease files, predictions, and knowledge base
- ✅ Environmental data tracking (temperature, soil metrics, UV index)
- ✅ Disease severity tracking and classification
- ✅ Treatment recommendations
- ✅ Advanced filtering capabilities
- ✅ SQLite database with SQLModel ORM
- ✅ Automatic database initialization
- ✅ CORS enabled for frontend integration
- ✅ Interactive API documentation (Swagger UI)

## Quick Start

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Installation

```bash
# Clone or navigate to the project
cd farmer_backend

# Install dependencies
pip install -r requirements.txt

# Or using uv (faster alternative)
uv pip install -r requirements.txt
```

### Running the Server

```bash
# Method 1: Using the startup script
python run_server.py

# Method 2: Direct uvicorn command
python -m uvicorn main:app --reload --port 8000
```

The server will start at: **http://localhost:8000**

### Access API Documentation
- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc

## API Endpoints

### 1. Disease Files API
Base path: `/api/disease-files`

#### Create Disease File
```
POST /api/disease-files/
Content-Type: application/json

{
  "crop_name": "Tomato",
  "image_path": "/images/tomato_001.jpg",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "notes": "Early blight symptoms",
  "weather": "hot",
  "temperature": 35.5,
  "soil_moisture": 65.0,
  "soil_temperature": 28.3,
  "soil_ph": 6.5,
  "uv_index": 8.5
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "crop_name": "Tomato",
  "image_path": "/images/tomato_001.jpg",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "notes": "Early blight symptoms",
  "weather": "hot",
  "temperature": 35.5,
  "soil_moisture": 65.0,
  "soil_temperature": 28.3,
  "soil_ph": 6.5,
  "uv_index": 8.5,
  "upload_dt": "2025-11-27T10:30:00"
}
```

#### Get All Disease Files
```
GET /api/disease-files/
```

**Response**: `200 OK` - Returns array of disease files

#### Get Disease File by ID
```
GET /api/disease-files/{id}
```

#### Update Disease File
```
PUT /api/disease-files/{id}
Content-Type: application/json

{
  "notes": "Updated notes"
}
```

**Response**: `200 OK` - Returns updated disease file

#### Delete Disease File
```
DELETE /api/disease-files/{id}
```

**Response**: `200 OK`

#### Filter Endpoints

**Filter by Crop Name**
```
GET /api/disease-files/filter-by-crop?crop_name=Tomato
```

**Filter by Weather**
```
GET /api/disease-files/filter-by-weather?weather=hot
```

**Filter by Temperature Range**
```
GET /api/disease-files/filter-by-temperature?min_temp=20&max_temp=35
```

**Filter by Soil Moisture Range**
```
GET /api/disease-files/filter-by-soil-moisture?min_moisture=40&max_moisture=80
```

**Filter by Soil Temperature Range**
```
GET /api/disease-files/filter-by-soil-temperature?min_temp=15&max_temp=30
```

**Filter by Soil pH Range**
```
GET /api/disease-files/filter-by-soil-ph?min_ph=6.0&max_ph=7.5
```

**Filter by UV Index Range**
```
GET /api/disease-files/filter-by-uv-index?min_uv=5&max_uv=10
```

---

### 2. Disease Predictions API
Base path: `/api/disease-predictions`

#### Create Disease Prediction
```
POST /api/disease-predictions/
Content-Type: application/json

{
  "disease_file_id": 1,
  "disease_name": "Early Blight",
  "accuracy": 0.92,
  "precision": 0.89,
  "recall": 0.88,
  "f_one_score": 0.885,
  "severity_score": 0.75,
  "severity_value": "high",
  "treatment": "Apply Mancozeb fungicide every 7-10 days"
}
```

**Response**: `201 Created`

#### Get All Disease Predictions
```
GET /api/disease-predictions/
```

#### Get Prediction by ID
```
GET /api/disease-predictions/{id}
```

#### Update Disease Prediction
```
PUT /api/disease-predictions/{id}
Content-Type: application/json

{
  "treatment": "Updated treatment recommendation"
}
```

#### Delete Disease Prediction
```
DELETE /api/disease-predictions/{id}
```

#### Filter Endpoints

**Filter by Disease Name**
```
GET /api/disease-predictions/filter-by-disease?disease_name=Early%20Blight
```

**Filter by Severity Level**
```
GET /api/disease-predictions/filter-by-severity?severity_level=high
```

Severity levels: `none`, `low`, `average`, `high`

**Filter by Accuracy Range**
```
GET /api/disease-predictions/filter-by-accuracy?min_accuracy=0.8&max_accuracy=1.0
```

**Filter by Precision Range**
```
GET /api/disease-predictions/filter-by-precision?min_precision=0.85&max_precision=1.0
```

---

### 3. Knowledge Base API
Base path: `/api/knowledge-base`

#### Create Knowledge Base Entry
```
POST /api/knowledge-base/
Content-Type: application/json

{
  "crop_name": "Potato",
  "disease_name": "Late Blight",
  "description": "Destructive disease of potato and tomato",
  "symptoms": "Water-soaked spots on leaves",
  "optimal_temperature": 18.0,
  "optimal_humidity": 85.0,
  "recommended_treatment": "Mancozeb fungicides",
  "prevention_methods": "Resistant varieties, crop rotation",
  "disease_file_id": 1,
  "severity_score": 0.85,
  "severity_value": "high"
}
```

**Response**: `201 Created`

#### Get All Knowledge Base Entries
```
GET /api/knowledge-base/
```

#### Get Knowledge Base Entry by ID
```
GET /api/knowledge-base/{kb_id}
```

#### Update Knowledge Base Entry
```
PUT /api/knowledge-base/{kb_id}
Content-Type: application/json

{
  "prevention_methods": "Updated prevention methods"
}
```

#### Delete Knowledge Base Entry
```
DELETE /api/knowledge-base/{kb_id}
```

#### Advanced Filter Endpoints

**Filter by Crop Name**
```
GET /api/knowledge-base/filter-by-crop?crop_name=Tomato
```

**Filter by Disease Name**
```
GET /api/knowledge-base/filter-by-disease?disease_name=Early%20Blight
```

**Filter by Severity Level**
```
GET /api/knowledge-base/filter-by-severity?severity_level=high
```

**Filter by Location (Bounding Box)**
```
GET /api/knowledge-base/filter-by-location?min_lat=28.0&max_lat=29.0&min_lon=77.0&max_lon=78.0
```

**Filter by Accuracy Range**
```
GET /api/knowledge-base/filter-by-accuracy?min_accuracy=0.85&max_accuracy=1.0
```

---

## Data Models

### DiseaseFilesModel
Represents a disease file record with environmental data.

```python
{
  "id": int,
  "crop_name": str,
  "image_path": str,
  "latitude": float,
  "longitude": float,
  "notes": str,
  "weather": str,  # "hot", "cold", "normal", "flood"
  "temperature": float,  # Optional, in Celsius
  "soil_moisture": float,  # Optional, percentage 0-100
  "soil_temperature": float,  # Optional, in Celsius
  "soil_ph": float,  # Optional, 0-14
  "uv_index": float,  # Optional
  "upload_dt": datetime
}
```

### DiseasePredictionModel
Represents a disease prediction with accuracy metrics.

```python
{
  "run_id": int,
  "disease_file_id": int,  # Foreign key
  "disease_name": str,
  "accuracy": float,  # 0.0-1.0
  "precision": float,  # 0.0-1.0
  "recall": float,  # 0.0-1.0
  "f_one_score": float,  # 0.0-1.0
  "severity_score": float,  # 0.0-1.0
  "severity_value": str,  # "none", "low", "average", "high"
  "treatment": str,
  "run_dt": datetime
}
```

### KnowledgeBaseModel
Comprehensive model combining disease files and prediction data.

```python
{
  "kb_id": int,
  "disease_file_id": int,
  "disease_prediction_id": int,  # Optional
  "crop_name": str,
  "disease_name": str,
  "description": str,
  "symptoms": str,
  "optimal_temperature": float,
  "optimal_humidity": float,
  "recommended_treatment": str,
  "prevention_methods": str,
  "severity_score": float,
  "severity_value": str,
  "accuracy": float,
  "precision": float,
  "recall": float,
  "f_one_score": float,
  "latitude": float,
  "longitude": float,
  "temperature": float,
  "soil_moisture": float,
  "soil_temperature": float,
  "soil_ph": float,
  "uv_index": float,
  "created_at": datetime,
  "updated_at": datetime
}
```

## Enums

### WeatherCondition
- `hot` - Hot weather
- `cold` - Cold weather
- `normal` - Normal weather
- `flood` - Flooding conditions

### SeverityLevel
- `none` - No severity
- `low` - Low severity
- `average` - Average severity
- `high` - High severity

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Successful GET/PUT/DELETE
- `201 Created` - Successful POST
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Testing

### Run Comprehensive Tests
```bash
python test_endpoints.py
```

This will:
- Test all CRUD operations
- Verify filtering endpoints
- Check database relationships
- Validate error handling

### Quick Health Check
```bash
python simple_test.py
```

## Database

- **Type**: SQLite
- **File**: `farmer_backend.db`
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Tables**: 
  - `diseasefilesmodel`
  - `diseasepredictionmodel`
  - `knowledgebasemodel`

### Database Initialization
The database is automatically created on server startup. Tables are initialized from model definitions.

## Project Structure

```
farmer_backend/
├── main.py                    # FastAPI app and routes
├── run_server.py             # Server startup script
├── requirements.txt          # Python dependencies
├── farmer_backend.db         # SQLite database
├── api/
│   ├── __init__.py
│   ├── disease_files.py      # Disease files endpoints
│   ├── disease_predictions.py # Predictions endpoints
│   └── knowledge_base.py      # Knowledge base endpoints
├── model/
│   ├── __init__.py
│   ├── database.py           # Database setup
│   ├── disease_files.py      # DiseaseFilesModel
│   ├── disease_prediction.py # DiseasePredictionModel
│   └── knowledge_base.py     # KnowledgeBaseModel
└── test/
    ├── test_endpoints.py     # Comprehensive API tests
    ├── test_api.py           # Additional tests
    └── test_setup.py         # Setup verification
```

## Development Tips

### Adding a New Endpoint
1. Create the endpoint function in the appropriate API file
2. Use the dependency injection `get_session()` for database access
3. Define input/output schemas using Pydantic BaseModel
4. Return appropriate HTTP status codes

### Database Queries
```python
from sqlmodel import Session, select
from model import DiseaseFilesModel

# In an endpoint function with Session dependency:
statement = select(DiseaseFilesModel).where(DiseaseFilesModel.crop_name == "Tomato")
results = session.exec(statement).all()
```

### Custom Filters
Follow the existing filter pattern in the API files:
1. Define filter parameters in endpoint query parameters
2. Build SQLAlchemy where clause dynamically
3. Return filtered results

## Support
For issues or questions, check the error logs in the terminal output when running `python run_server.py`.

## Version
API Version: 0.1.0
Last Updated: November 2025
