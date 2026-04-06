# Developer's Quick Reference Card

## 🚀 Quick Commands

```bash
# Start server
python run_server.py

# Validate setup
python validate.py

# Run tests
python test_endpoints.py

# Quick test
python simple_test.py

# Direct uvicorn
python -m uvicorn main:app --reload --port 8000
```

## 📍 Key URLs

| Purpose | URL |
|---------|-----|
| API Root | http://localhost:8000 |
| Health Check | http://localhost:8000/health |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

## 📚 API Base Paths

| Resource | Base Path |
|----------|-----------|
| Disease Files | `/api/disease-files` |
| Predictions | `/api/disease-predictions` |
| Knowledge Base | `/api/knowledge-base` |

## 🔧 CRUD Endpoints Pattern

### For All Resources

```
POST   /api/{resource}/              Create
GET    /api/{resource}/              List all
GET    /api/{resource}/{id}          Get one
PUT    /api/{resource}/{id}          Update
DELETE /api/{resource}/{id}          Delete
```

Replace `{resource}` with:
- `disease-files`
- `disease-predictions`
- `knowledge-base`

## 🎯 Most Used Endpoints

### Create Disease File
```bash
POST /api/disease-files/
Content-Type: application/json

{
  "crop_name": "Tomato",
  "image_path": "/path",
  "latitude": 28.6,
  "longitude": 77.2,
  "notes": "symptoms",
  "weather": "hot",
  "temperature": 35.5
}
```

### Create Prediction
```bash
POST /api/disease-predictions/
{
  "disease_file_id": 1,
  "disease_name": "Early Blight",
  "accuracy": 0.92,
  "severity_value": "high",
  "treatment": "Apply fungicide"
}
```

### Filter by Severity
```bash
GET /api/disease-predictions/filter-by-severity?severity_level=high
```

## 🗄️ Database Models

### DiseaseFilesModel
```python
id: int (PK)
crop_name: str
image_path: str
latitude: float
longitude: float
notes: str
weather: WeatherCondition
temperature: float
soil_moisture: float
soil_temperature: float
soil_ph: float
uv_index: float
upload_dt: datetime
```

### DiseasePredictionModel
```python
run_id: int (PK)
disease_file_id: int (FK)
disease_name: str
accuracy: float (0-1)
precision: float (0-1)
recall: float (0-1)
f_one_score: float (0-1)
severity_score: float (0-1)
severity_value: SeverityLevel
treatment: str
run_dt: datetime
```

### KnowledgeBaseModel
```python
kb_id: int (PK)
disease_file_id: int (FK)
disease_prediction_id: int (FK, optional)
[All fields from both above models]
```

## 📊 Enums

### WeatherCondition
```python
"hot"
"cold"
"normal"
"flood"
```

### SeverityLevel
```python
"none"
"low"
"average"
"high"
```

## 🔍 All Filter Endpoints

### Disease Files Filters
```
/filter-by-crop?crop_name=Tomato
/filter-by-weather?weather=hot
/filter-by-temperature?min_temp=20&max_temp=35
/filter-by-soil-moisture?min_moisture=40&max_moisture=80
/filter-by-soil-temperature?min_temp=15&max_temp=30
/filter-by-soil-ph?min_ph=6.0&max_ph=7.5
/filter-by-uv-index?min_uv=5&max_uv=10
/filter-by-date-range?start_date=2025-01-01&end_date=2025-12-31
```

### Predictions Filters
```
/filter-by-disease?disease_name=Early%20Blight
/filter-by-severity?severity_level=high
/filter-by-accuracy?min_accuracy=0.8&max_accuracy=1.0
/filter-by-precision?min_precision=0.85&max_precision=1.0
/filter-by-recall?min_recall=0.85&max_recall=1.0
/filter-by-f1-score?min_f1=0.85&max_f1=1.0
```

### Knowledge Base Filters
```
/filter-by-crop?crop_name=Potato
/filter-by-disease?disease_name=Late%20Blight
/filter-by-severity?severity_level=high
/filter-by-location?min_lat=28&max_lat=29&min_lon=77&max_lon=78
/filter-by-accuracy?min_accuracy=0.85&max_accuracy=1.0
/filter-by-created-date?start_date=2025-01-01&end_date=2025-12-31
/search?q=search%20term
```

## 🧪 Testing

```bash
# Full validation
python validate.py

# API tests (server must be running)
python test_endpoints.py

# Database test
python test_setup.py

# Quick test
python simple_test.py
```

## 🔧 Common Configuration Changes

### Change Database Path
**File**: `model/database.py`
```python
DATABASE_URL = "sqlite:///./your_path.db"
```

### Change Server Port
**File**: `run_server.py`
```python
--port 9000  # Change 8000 to 9000
```

### Enable SQL Logging
**File**: `model/database.py`
```python
echo=True  # Change False to True
```

### Restrict CORS
**File**: `main.py`
```python
allow_origins=["http://localhost:3000", "https://yoursite.com"]
```

## 📁 Project Structure Quick View

```
model/          → Data models
  ├─ database.py
  ├─ disease_files.py
  ├─ disease_prediction.py
  └─ knowledge_base.py

api/            → API endpoints
  ├─ disease_files.py
  ├─ disease_predictions.py
  └─ knowledge_base.py

main.py         → FastAPI app
run_server.py   → Server startup
validate.py     → Validation
requirements.txt → Dependencies
```

## 🔐 HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| 200 | OK (Successful GET/PUT/DELETE) |
| 201 | Created (Successful POST) |
| 400 | Bad Request (Invalid input) |
| 404 | Not Found (Resource not found) |
| 500 | Server Error (Internal error) |

## 🐛 Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Port 8000 in use | `python -m uvicorn main:app --port 8001` |
| Database locked | `rm farmer_backend.db` then restart |
| Import errors | `pip install --upgrade -r requirements.txt` |
| CORS errors | Check `main.py` CORS configuration |
| 404 errors | Check URL spelling and base path |
| Validation fails | Run: `python validate.py` to diagnose |

## 💡 Common Code Patterns

### Access Database in Endpoint
```python
@router.get("/")
def get_all(session: Session = Depends(get_session)):
    statement = select(DiseaseFilesModel)
    return session.exec(statement).all()
```

### Create New Record
```python
@router.post("/", response_model=DiseaseFilesRead, status_code=status.HTTP_201_CREATED)
def create(item: DiseaseFilesCreate, session: Session = Depends(get_session)):
    db_item = DiseaseFilesModel.from_orm(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

### Filter Records
```python
statement = select(DiseaseFilesModel).where(
    DiseaseFilesModel.crop_name == crop_name
)
results = session.exec(statement).all()
```

### Update Record
```python
db_item = session.get(DiseaseFilesModel, item_id)
db_item.notes = "New notes"
session.add(db_item)
session.commit()
session.refresh(db_item)
return db_item
```

## 📖 Documentation Files Map

| File | Purpose |
|------|---------|
| README.md | Project overview |
| API_DOCUMENTATION.md | Complete API reference |
| QUICKSTART.md | 5-minute setup |
| IMPLEMENTATION_SUMMARY.md | Technical overview |
| DEPLOYMENT_GUIDE.md | Production deployment |
| DELIVERY_PACKAGE.md | What's included |
| QUICK_REFERENCE.md | This file |

## 🔗 Important Import Statements

```python
# Models
from model import (
    DiseaseFilesModel,
    DiseasePredictionModel,
    KnowledgeBaseModel,
    WeatherCondition,
    SeverityLevel,
    get_session,
    create_db_and_tables
)

# FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# SQLModel
from sqlmodel import Session, select

# Pydantic
from pydantic import BaseModel
```

## 🎯 Development Workflow

1. **Start Server**
   ```bash
   python run_server.py
   ```

2. **Access Documentation**
   - Browser: http://localhost:8000/docs

3. **Test Endpoint**
   - Try it in Swagger UI

4. **Check Logs**
   - Look at terminal output

5. **Debug**
   - Add `print()` statements
   - Check error messages
   - Run `python validate.py`

## 📞 Need Help?

1. Run validation: `python validate.py`
2. Check docs: http://localhost:8000/docs
3. Read: API_DOCUMENTATION.md
4. Read: QUICKSTART.md
5. Check server logs in terminal

## ✨ Key Features at a Glance

✅ 38 API endpoints
✅ Complete CRUD operations
✅ Advanced filtering
✅ Environmental tracking
✅ Severity management
✅ Type-safe database
✅ Automatic documentation
✅ Production ready
✅ Zero configuration
✅ Fully tested

---

**Last Updated**: November 27, 2025
**Version**: 0.1.0
**Status**: Production Ready ✅
