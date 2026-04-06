# Farmer Backend - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+ installed
- Git (optional, for cloning)

### Step 1: Install Dependencies
```bash
cd farmer_backend
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python run_server.py
```

You should see:
```
===================================================
Starting Farmer Backend API Server...
===================================================

Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs
Interactive API: http://localhost:8000/redoc
```

### Step 3: Open API Documentation
Visit **http://localhost:8000/docs** in your browser to access the interactive Swagger UI.

---

## 📋 What You Have

### 38 API Endpoints Across 3 Resources

#### Disease Files (13 endpoints)
- CRUD operations for disease file records
- Filters by: crop, weather, temperature, soil moisture, soil temperature, pH, UV index

#### Disease Predictions (12 endpoints)
- CRUD operations for disease predictions
- Filters by: disease name, severity level, accuracy, precision

#### Knowledge Base (13 endpoints)
- CRUD operations for comprehensive disease information
- Advanced filters by: crop, disease, severity, location, accuracy

### Database
- **SQLite**: Lightweight, zero-configuration database
- **SQLModel**: Type-safe ORM with Pydantic validation
- **Auto-initialization**: Tables created automatically on startup

---

## 🧪 Testing

### Validation Check
```bash
python validate.py
```
Shows detailed validation of all components.

### Comprehensive API Tests
```bash
python test_endpoints.py
```
Tests all endpoints with real data (requires server running).

### Quick Smoke Test
```bash
python simple_test.py
```
Quick test of core functionality.

---

## 📚 API Examples

### Create a Disease File
```bash
curl -X POST "http://localhost:8000/api/disease-files/" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Tomato",
    "image_path": "/images/tomato.jpg",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "notes": "Early blight symptoms",
    "weather": "hot",
    "temperature": 35.5,
    "soil_moisture": 65.0,
    "soil_temperature": 28.3,
    "soil_ph": 6.5,
    "uv_index": 8.5
  }'
```

### Get All Disease Files
```bash
curl "http://localhost:8000/api/disease-files/"
```

### Create a Disease Prediction
```bash
curl -X POST "http://localhost:8000/api/disease-predictions/" \
  -H "Content-Type: application/json" \
  -d '{
    "disease_file_id": 1,
    "disease_name": "Early Blight",
    "accuracy": 0.92,
    "precision": 0.89,
    "recall": 0.88,
    "f_one_score": 0.885,
    "severity_score": 0.75,
    "severity_value": "high",
    "treatment": "Apply Mancozeb fungicide every 7-10 days"
  }'
```

### Filter by Crop
```bash
curl "http://localhost:8000/api/disease-files/filter-by-crop?crop_name=Tomato"
```

### Filter by Severity
```bash
curl "http://localhost:8000/api/disease-predictions/filter-by-severity?severity_level=high"
```

---

## 🏗️ Project Structure

```
farmer_backend/
├── main.py                         # FastAPI application
├── run_server.py                   # Server startup script
├── validate.py                     # Validation script
├── requirements.txt                # Python dependencies
├── farmer_backend.db              # SQLite database
│
├── model/                          # Data models
│   ├── __init__.py
│   ├── database.py                # Database setup
│   ├── disease_files.py           # DiseaseFilesModel
│   ├── disease_prediction.py      # DiseasePredictionModel
│   └── knowledge_base.py          # KnowledgeBaseModel
│
├── api/                           # API endpoints
│   ├── __init__.py
│   ├── disease_files.py           # Disease files CRUD
│   ├── disease_predictions.py     # Predictions CRUD
│   └── knowledge_base.py          # Knowledge base CRUD
│
├── test/                          # Test files
│   ├── test_endpoints.py
│   ├── test_api.py
│   └── test_setup.py
│
└── docs/                          # Documentation
    ├── API_DOCUMENTATION.md
    └── QUICKSTART.md
```

---

## 🔧 Configuration

### Database Location
The SQLite database is stored at: `./farmer_backend.db`

To use a different location, edit `model/database.py`:
```python
DATABASE_URL = "sqlite:///./farmer_backend.db"  # Change this path
```

### Server Port
To use a different port, modify the `run_server.py`:
```python
# Change --port 8000 to your desired port
subprocess.run(
    [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "9000"],
    ...
)
```

---

## 📖 Detailed Documentation

For complete API documentation, see: **API_DOCUMENTATION.md**

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python -m uvicorn main:app --port 8001
```

### Database Error
```bash
# Delete the database file and restart (creates fresh database)
rm farmer_backend.db
python run_server.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📦 Deployment

### Production Setup
For production deployment, use a production-grade ASGI server:

```bash
# Install Gunicorn with Uvicorn workers
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t farmer-backend .
docker run -p 8000:8000 farmer-backend
```

---

## 🤝 Integration with Frontend

### CORS is Already Enabled
The backend allows requests from any origin (development-friendly).

### Connect from Frontend
```javascript
const API_URL = "http://localhost:8000/api";

// Example: Create disease file
async function createDiseaseFile(data) {
  const response = await fetch(`${API_URL}/disease-files/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return response.json();
}
```

---

## 📊 Data Models Overview

### DiseaseFilesModel
Stores disease file records with environmental data:
- Crop information
- Image path
- GPS coordinates
- Weather conditions
- Environmental metrics (temperature, humidity, pH, etc.)
- Upload timestamp

### DiseasePredictionModel
Stores ML prediction results:
- Disease prediction
- Accuracy metrics (accuracy, precision, recall, F1)
- Severity classification
- Treatment recommendations
- Prediction timestamp

### KnowledgeBaseModel
Comprehensive combination of both models:
- Complete disease information
- Environmental context
- Prediction metrics
- Integrated search and filtering

---

## ✅ Validation Checklist

Run this to verify everything is working:

```bash
python validate.py
```

Expected output:
```
✓ All validations passed! Backend is ready to run.
ℹ To start the server, run: python run_server.py
```

---

## 🎯 Next Steps

1. **Start the server**: `python run_server.py`
2. **Explore API**: Visit http://localhost:8000/docs
3. **Test endpoints**: Use the interactive Swagger UI
4. **Create frontend**: Connect to these endpoints from your React/Vue/Angular app
5. **Deploy**: Use Docker or traditional server deployment

---

## 📞 Support

For issues:
1. Check the terminal output when running `python run_server.py`
2. Review `API_DOCUMENTATION.md` for endpoint details
3. Run `python validate.py` to check configuration
4. Check error messages in the HTTP response

---

## Version Info
- **API Version**: 0.1.0
- **FastAPI**: 0.115.12
- **SQLModel**: Latest
- **Python**: 3.10+
- **Last Updated**: November 2025

---

**Happy farming! 🌾**
