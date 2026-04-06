# Farmer Backend API 🌾

A comprehensive FastAPI backend for managing crop diseases, environmental data, and disease predictions with a SQLite database.

## ✨ Features

- **38 API Endpoints** across 3 main resources
- **Complete CRUD Operations** for disease files, predictions, and knowledge base
- **Advanced Filtering** by crop, disease, severity, accuracy, location, and environmental conditions
- **Environmental Tracking** - temperature, soil metrics, UV index, weather conditions
- **Disease Severity Scoring** - quantitative disease severity assessment
- **Treatment Recommendations** - ML-based treatment suggestions
- **Type-Safe Database** - SQLModel ORM with Pydantic validation
- **Automatic Schema Generation** - Interactive API documentation with Swagger UI
- **Production-Ready** - CORS enabled, proper error handling, database persistence
- **Zero-Configuration Setup** - Automatic database initialization

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Installation & Running

```bash
# Clone/navigate to project
cd farmer_backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python run_server.py
```

**Server will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Interactive Swagger UI)
- ReDoc: http://localhost:8000/redoc

## 📚 API Resources

### Disease Files
Manage disease file records with environmental data

**Endpoints:**
- `POST /api/disease-files/` - Create
- `GET /api/disease-files/` - List all
- `GET /api/disease-files/{id}` - Get by ID
- `PUT /api/disease-files/{id}` - Update
- `DELETE /api/disease-files/{id}` - Delete
- Multiple filter endpoints for crop, weather, temperature, soil conditions, etc.

### Disease Predictions
Manage ML disease predictions with accuracy metrics

**Endpoints:**
- `POST /api/disease-predictions/` - Create
- `GET /api/disease-predictions/` - List all
- `GET /api/disease-predictions/{id}` - Get by ID
- `PUT /api/disease-predictions/{id}` - Update
- `DELETE /api/disease-predictions/{id}` - Delete
- Filter endpoints for disease name, severity level, accuracy ranges

### Knowledge Base
Comprehensive disease information combining files and predictions

**Endpoints:**
- Full CRUD operations
- Advanced filtering by crop, disease, severity, location, accuracy

## 🧪 Testing

### Validate Setup
```bash
python validate.py
```

### Run Full API Tests
```bash
python test_endpoints.py
```

### Quick Health Check
```bash
python simple_test.py
```

## 🏗️ Project Structure

```
farmer_backend/
├── main.py                      # FastAPI app
├── run_server.py               # Server startup
├── validate.py                 # Validation tool
├── requirements.txt            # Dependencies
├── farmer_backend.db           # SQLite database
│
├── model/                      # Data models
│   ├── database.py
│   ├── disease_files.py
│   ├── disease_prediction.py
│   └── knowledge_base.py
│
├── api/                        # API endpoints
│   ├── disease_files.py
│   ├── disease_predictions.py
│   └── knowledge_base.py
│
└── test/                       # Tests
    ├── test_endpoints.py
    ├── test_api.py
    └── test_setup.py
```

## 📦 Deployment

### Development
```bash
python run_server.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```bash
docker build -t farmer-backend .
docker run -p 8000:8000 farmer-backend
```

## 📖 Documentation

- **Full API Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Quick Start Guide**: [QUICKSTART.md](./QUICKSTART.md)
- **Interactive Docs**: http://localhost:8000/docs (when server running)

## 🎯 Quick Example

```bash
# Create a disease file
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
    "soil_moisture": 65.0
  }'
```

## 🔧 Configuration

**Database**: Edit `model/database.py` to change path
**Port**: Edit `run_server.py` to use different port

## ✅ Validation

```bash
python validate.py
```

Expected: All 7 checks passed

## 📊 Statistics

- **38 Total Endpoints**
- **3 Main Data Models**
- **Multiple Filter Capabilities**
- **Full Type Safety**

## 📞 Support

- Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- Run `python validate.py`
- Visit http://localhost:8000/docs

---

**Made for Farmers 🌾 | Built with FastAPI ⚡**

Version: 0.1.0 | Updated: November 2025
