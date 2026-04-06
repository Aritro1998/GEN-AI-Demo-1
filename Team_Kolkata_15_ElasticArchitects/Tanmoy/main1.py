# API Endpoints (The Entry Point)

from fastapi import FastAPI, HTTPException, Depends, Request, Header, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from repository.user_repository import UserRepository
from repository.service import PlantDiseaseService
from repository.analytics_service import AnalyticsService
from models import *
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthManager, authenticate_token, require_farmer_or_admin, require_admin_only
from dbhandler import get_db
from sqlalchemy.orm import Session
import json, os, base64
from typing import Optional, List
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

app = FastAPI(title="Plant Disease Detection System", version="2.0")
user_repo = UserRepository()
disease_service = PlantDiseaseService()
analytics_service = AnalyticsService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    JWT_SECRET = config.get('JWT_SECRET', 'secret-key')
    JWT_ALGORITHM = config.get('JWT_ALGORITHM', 'HS256')
else:
    JWT_SECRET = 'secret-key'
    JWT_ALGORITHM = 'HS256'

auth_manager = AuthManager(JWT_SECRET, JWT_ALGORITHM)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# ==================== EXISTING USER MANAGEMENT ENDPOINTS ====================

@app.post('/create')
def create_user(user: UserCreate, x_access_token: str = Header(...)):
    """Create new user (admin only in production)"""
    authenticate_token(auth_manager, x_access_token)
    user_repo.create_user(
        user.username, user.password, user.firstname, 
        user.lastname, user.created_by, user.user_role
    )
    return {"message": "User created"}

@app.delete('/delete/{username}')
def delete_user(username: str, x_access_token: str = Header(...)):
    authenticate_token(auth_manager, x_access_token)
    user_repo.delete_user(username)
    return {"message": "User deleted"}

@app.post('/unlock/{username}')
def unlock_user(username: str, x_access_token: str = Header(...)):
    authenticate_token(auth_manager, x_access_token)
    user_repo.unlock_user(username)
    return {"message": "User unlocked"}

@app.post('/changepwd')
def change_password(data: ChangePwd, x_access_token: str = Header(...)):
    authenticate_token(auth_manager, x_access_token)
    user_repo.change_password(data.username, data.new_password)
    return {"message": "Password changed"}

@app.post('/login')
def login(user: UserLogin):
    """Login endpoint - returns token in header"""
    token, role = user_repo.login(user.username, user.password)
    if not token:
        raise HTTPException(status_code=401, detail=role)
    
    response = {
        "message": "Login successful",
        "username": user.username,
        "role": role
    }
    headers = {"x-access-token": token}
    return JSONResponse(content=response, headers=headers)

@app.get('/users')
def get_all_users(x_access_token: str = Header(...)):
    authenticate_token(auth_manager, x_access_token)
    users = user_repo.get_all_users()
    return {"users": users}

@app.get('/current_user')
def get_current_user(x_access_token: str = Header(...)):
    """Get current logged-in user info"""
    payload = authenticate_token(auth_manager, x_access_token)
    return {
        "user_id": payload.get('user_id'),
        "username": payload.get('username'),
        "role": payload.get('role')
    }

# ==================== FARMER ENDPOINTS ====================

@app.get('/api/v1/farmer/dashboard')
def get_farmer_dashboard(
    x_access_token: str = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Home/Dashboard: Last 3 diagnoses + stats"""
    user_id = x_access_token.get('user_id')
    
    recent_diagnoses = db.query(DiagnosisRecord).filter(
        DiagnosisRecord.user_id == user_id
    ).order_by(DiagnosisRecord.timestamp.desc()).limit(3).all()
    
    total_count = db.query(DiagnosisRecord).filter(
        DiagnosisRecord.user_id == user_id
    ).count()
    
    return {
        "user_id": user_id,
        "username": x_access_token.get('username'),
        "recent_diagnoses": [
            {
                "id": d.id,
                "diagnosis": d.diagnosis,
                "risk_level": d.risk_level,
                "timestamp": d.timestamp.isoformat(),
                "severity_percent": d.severity_percent
            } for d in recent_diagnoses
        ],
        "total_diagnoses": total_count,
        "weather": {"temp": 28, "humidity": 65}  # Integrate real weather API
    }

@app.post('/api/v1/farmer/diagnose')
async def diagnose_plant_disease(
    image: UploadFile = File(...),
    crop: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    user_notes: Optional[str] = Form(None),
    temperature: Optional[float] = Form(None),
    humidity: Optional[float] = Form(None),
    soil_moisture: Optional[float] = Form(None),
    x_access_token: str = Header(...),
    db: Session = Depends(get_db)
):
    """Core diagnosis endpoint - replaces /detect"""
    payload = authenticate_token(auth_manager, x_access_token)
    user_id = payload.get('user_id')
    
    # Read and encode image
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Save image
    timestamp = datetime.utcnow().timestamp()
    os.makedirs("data/images", exist_ok=True)
    image_path = f"data/images/{user_id}_{timestamp}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    
    # Prepare environmental data
    env_data = None
    if temperature or humidity or soil_moisture:
        env_data = {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture
        }
    
    # Run AI analysis
    result = await disease_service.analyze_plant_image(
        image_data=image_base64,
        crop_type=crop,
        environmental_data=env_data
    )
    
    # Store diagnosis in database
    diagnosis = DiagnosisRecord(
        user_id=user_id,
        image_path=image_path,
        crop=crop,
        diagnosis=result['disease'],
        disease_category=result['disease_category'],
        severity_percent=result['infection_percentage'],
        confidence_score=result['confidence'],
        risk_level=result['risk_level'],
        action_plan_text=result['action_plan_text'],
        weather_context=env_data,
        latitude=latitude,
        longitude=longitude,
        user_notes=user_notes
    )
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    
    return {
        "id": diagnosis.id,
        "disease": diagnosis.diagnosis,
        "severity_percent": diagnosis.severity_percent,
        "confidence": diagnosis.confidence_score,
        "risk_level": diagnosis.risk_level,
        "action_plan": diagnosis.action_plan_text,
        "timestamp": diagnosis.timestamp.isoformat()
    }

@app.get('/api/v1/farmer/records')
def get_my_records(
    skip: int = 0,
    limit: int = 50,
    crop_filter: Optional[str] = None,
    x_access_token: str = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """My Records/History"""
    user_id = x_access_token.get('user_id')
    
    query = db.query(DiagnosisRecord).filter(DiagnosisRecord.user_id == user_id)
    
    if crop_filter:
        query = query.filter(DiagnosisRecord.crop == crop_filter)
    
    records = query.order_by(DiagnosisRecord.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "records": [
            {
                "id": r.id,
                "diagnosis": r.diagnosis,
                "crop": r.crop,
                "severity_percent": r.severity_percent,
                "risk_level": r.risk_level,
                "timestamp": r.timestamp.isoformat()
            } for r in records
        ]
    }

@app.get('/api/v1/farmer/knowledge-base')
def get_knowledge_base(
    search: Optional[str] = None,
    crop_filter: Optional[str] = None,
    x_access_token: str = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Knowledge Base: Searchable diseases and treatments"""
    diseases_query = db.query(Disease)
    treatments_query = db.query(Treatment)
    
    if crop_filter:
        diseases_query = diseases_query.filter(Disease.crop_name == crop_filter)
    
    if search:
        diseases_query = diseases_query.filter(Disease.name.contains(search))
        treatments_query = treatments_query.filter(Treatment.name.contains(search))
    
    return {
        "diseases": [
            {
                "id": d.id,
                "name": d.name,
                "crop": d.crop_name,
                "symptoms": d.symptoms,
                "causal_agent": d.causal_agent
            } for d in diseases_query.limit(20).all()
        ],
        "treatments": [
            {
                "id": t.id,
                "name": t.name,
                "type": t.type,
                "application_rate": t.application_rate,
                "instructions": t.instructions
            } for t in treatments_query.limit(20).all()
        ]
    }

# ==================== ADMIN ENDPOINTS ====================

@app.get('/api/v1/admin/dashboard')
async def get_admin_dashboard(
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Admin Overview/KPI Dashboard"""
    return await analytics_service.get_kpi_dashboard(db)

@app.get('/api/v1/admin/outbreak-map')
async def get_outbreak_map(
    risk_level: Optional[str] = None,
    crop_filter: Optional[str] = None,
    days_back: int = 30,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Outbreak Prediction Map"""
    return await analytics_service.get_outbreak_map(
        db, risk_level=risk_level, crop_filter=crop_filter, days_back=days_back
    )

@app.get('/api/v1/admin/diagnoses')
def get_all_diagnoses(
    skip: int = 0,
    limit: int = 100,
    unvalidated_only: bool = False,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Raw Diagnosis Records for validation"""
    query = db.query(DiagnosisRecord)
    
    if unvalidated_only:
        query = query.filter(DiagnosisRecord.admin_validated == False)
    
    records = query.order_by(DiagnosisRecord.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "records": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "crop": r.crop,
                "diagnosis": r.diagnosis,
                "severity_percent": r.severity_percent,
                "risk_level": r.risk_level,
                "timestamp": r.timestamp.isoformat(),
                "image_path": r.image_path,
                "validated": r.admin_validated
            } for r in records
        ]
    }

@app.post('/api/v1/admin/feedback')
def submit_admin_feedback(
    feedback: AdminFeedbackCreate,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Submit validation feedback on diagnosis"""
    admin_id = x_access_token.get('user_id')
    
    admin_feedback = AdminFeedback(
        diagnosis_id=feedback.diagnosis_id,
        admin_id=admin_id,
        is_correct=feedback.is_correct,
        corrected_diagnosis=feedback.corrected_diagnosis,
        corrected_severity=feedback.corrected_severity,
        notes=feedback.notes
    )
    db.add(admin_feedback)
    
    # Mark diagnosis as validated
    diagnosis = db.query(DiagnosisRecord).filter(
        DiagnosisRecord.id == feedback.diagnosis_id
    ).first()
    if diagnosis:
        diagnosis.admin_validated = True
    
    db.commit()
    return {"message": "Feedback submitted successfully"}

@app.post('/api/v1/admin/diseases')
def create_disease(
    disease: DiseaseCreate,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Add new disease to knowledge base"""
    new_disease = Disease(**disease.dict())
    db.add(new_disease)
    db.commit()
    db.refresh(new_disease)
    return new_disease

@app.put('/api/v1/admin/diseases/{disease_id}')
def update_disease(
    disease_id: int,
    disease: DiseaseCreate,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Update disease information"""
    existing = db.query(Disease).filter(Disease.id == disease_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Disease not found")
    
    for key, value in disease.dict().items():
        setattr(existing, key, value)
    
    db.commit()
    return {"message": "Disease updated successfully"}

@app.post('/api/v1/admin/treatments')
def create_treatment(
    treatment: TreatmentCreate,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Add new treatment"""
    new_treatment = Treatment(**treatment.dict())
    db.add(new_treatment)
    db.commit()
    db.refresh(new_treatment)
    return new_treatment

@app.get('/api/v1/admin/analytics')
async def get_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    x_access_token: str = Depends(require_admin_only),
    db: Session = Depends(get_db)
):
    """Analytics & Reporting"""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    return await analytics_service.get_analytics_report(db, start, end)

# ==================== LEGACY ENDPOINTS (Keep for backwards compatibility) ====================

@app.post('/detect')
def detect_disease_legacy(image: UploadFile = File(...)):
    """Legacy endpoint - redirects to new diagnosis flow"""
    return {
        "message": "Please use /api/v1/farmer/diagnose endpoint",
        "disease": "rust",
        "severity": 0.7,
        "confidence": 0.95,
        "recommendations": ["Use new endpoint for full diagnosis"]
    }

@app.get('/diseases')
def get_diseases():
    """Legacy endpoint - basic disease list"""
    diseases = [
        {"name": "rust", "description": "Fungal disease causing reddish spots."},
        {"name": "mildew", "description": "White powdery growth on leaves."},
        {"name": "blight", "description": "Rapid tissue death."}
    ]
    return {"diseases": diseases}
