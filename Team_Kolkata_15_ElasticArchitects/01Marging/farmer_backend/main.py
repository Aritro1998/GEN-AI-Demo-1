import json
import os
from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from sqlmodel import Session

from auth import AuthManager, authenticate_token, require_admin_only
from dbhandler import get_db, init_db
from models import ChangePwd, DiagnosisRecord, UserCreate, UserLogin
from repository.analytics_service import AnalyticsService
from repository.service import PlantDiseaseService
from model import create_db_and_tables
from api import disease_files_router, disease_predictions_router, knowledge_base_router
from repository.user_repository import UserRepository

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()  # Initialize SQLModel tables (disease files, predictions, knowledge base)
    init_db()  # Initialize SQLAlchemy tables (users, diagnoses, feedbacks, etc.)
    print("Database initialized on startup")
    yield
    # Shutdown
    print("Application shutting down")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

user_repo = UserRepository()
disease_service = PlantDiseaseService()
analytics_service = AnalyticsService()

# Create FastAPI app with lifespan
app = FastAPI(
    title="Farmer Backend API",
    description="API for managing disease files with crop information and weather conditions",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(disease_files_router)
app.include_router(disease_predictions_router)
app.include_router(knowledge_base_router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Farmer Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

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
def create_user(user: UserCreate):
    """Create new user (admin only in production)"""
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

def main():
    print("Farmer Backend Server started!")


if __name__ == "__main__":
    main()
