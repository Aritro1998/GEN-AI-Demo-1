# DB Tables & Pydantic Schemas
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import enum

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DiseaseCategory(str, enum.Enum):
    RUST = "rust"
    MILDEW = "mildew"
    BLIGHT = "blight"
    SPOT = "spot"
    MOSAIC = "mosaic"
    HEALTHY = "healthy"

# ==================== DATABASE TABLES ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    firstname = Column(String)  # Fixed typo
    lastname = Column(String)
    user_role = Column(String, default="farmer")  # "farmer" or "admin"
    created_by = Column(String)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    
    # Relationships
    diagnoses = relationship("DiagnosisRecord", back_populates="user")
    feedbacks = relationship("AdminFeedback", back_populates="admin")

class DiagnosisRecord(Base):
    __tablename__ = "diagnosis_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Image & Location
    image_path = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Core Diagnosis
    crop = Column(String, index=True)
    diagnosis = Column(String, index=True)
    disease_category = Column(String)
    severity_percent = Column(Float)
    confidence_score = Column(Float)
    
    # Risk & Context
    risk_level = Column(String, index=True)
    action_plan_text = Column(Text)
    weather_context = Column(JSON, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_notes = Column(Text, nullable=True)
    processed_offline = Column(Boolean, default=False)
    
    # Admin Validation
    admin_validated = Column(Boolean, default=False)
    admin_feedback_id = Column(Integer, ForeignKey("admin_feedbacks.id"), nullable=True)
    
    # Relationships - FIXED
    user = relationship("User", back_populates="diagnoses")
    # Remove the problematic relationship - we'll access feedback via admin_feedback_id directly

class Disease(Base):
    __tablename__ = "diseases"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    crop_name = Column(String, index=True)
    causal_agent = Column(String)
    symptoms = Column(Text)
    common_names = Column(JSON)
    image_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Treatment(Base):
    __tablename__ = "treatments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    type = Column(String)
    application_rate = Column(String)
    active_ingredient = Column(String, nullable=True)
    target_diseases = Column(JSON)
    safety_period_days = Column(Integer, nullable=True)
    instructions = Column(Text)
    cost_estimate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class AdminFeedback(Base):
    __tablename__ = "admin_feedbacks"
    
    id = Column(Integer, primary_key=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnosis_records.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    
    is_correct = Column(Boolean)
    corrected_diagnosis = Column(String, nullable=True)
    corrected_severity = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships - FIXED
    admin = relationship("User", back_populates="feedbacks", foreign_keys=[admin_id])
    
# ==================== PYDANTIC SCHEMAS ====================

# Existing schemas (kept as-is)
class UserCreate(BaseModel):
    username: str
    password: str
    firstname: str  # Fixed typo
    lastname: str
    created_by: str
    user_role: str = "farmer"  # farmer or admin
    location: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ChangePwd(BaseModel):
    username: str
    new_password: str

# New schemas for plant disease system
class DiagnosisRequest(BaseModel):
    crop: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_notes: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None

class DiagnosisResponse(BaseModel):
    id: int
    diagnosis: str
    disease_category: str
    severity_percent: float
    confidence_score: float
    risk_level: str
    action_plan_text: str
    timestamp: datetime
    weather_context: Optional[dict]
    
    class Config:
        from_attributes = True

class DiagnosisListItem(BaseModel):
    id: int
    diagnosis: str
    crop: str
    risk_level: str
    timestamp: datetime
    severity_percent: float

class DiseaseCreate(BaseModel):
    name: str
    crop_name: str
    causal_agent: str
    symptoms: str
    common_names: list[str] = []

class TreatmentCreate(BaseModel):
    name: str
    type: str
    application_rate: str
    active_ingredient: Optional[str] = None
    target_diseases: list[str]
    instructions: str

class AdminFeedbackCreate(BaseModel):
    diagnosis_id: int
    is_correct: bool
    corrected_diagnosis: Optional[str] = None
    corrected_severity: Optional[float] = None
    notes: Optional[str] = None
