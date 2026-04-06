from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
from enum import Enum


class WeatherCondition(str, Enum):
    """Enum for weather conditions"""
    HOT = "hot"
    COLD = "cold"
    NORMAL = "normal"
    FLOOD = "flood"


class SeverityLevel(str, Enum):
    """Enum for disease severity levels"""
    NONE = "none"
    LOW = "low"
    AVERAGE = "average"
    HIGH = "high"


class KnowledgeBaseModel(SQLModel, table=True):
    """
    Comprehensive knowledge base combining disease files and prediction data.
    This model aggregates information from both DiseaseFilesModel and DiseasePredictionModel
    for easy access to complete disease diagnosis and environmental context.
    """
    
    # Primary key and foreign keys
    kb_id: Optional[int] = Field(default=None, primary_key=True, description="Knowledge base record ID")
    disease_file_id: int = Field(
        foreign_key="diseasefilesmodel.id",
        description="Foreign key reference to DiseaseFilesModel"
    )
    disease_prediction_id: Optional[int] = Field(
        default=None,
        description="Foreign key reference to DiseasePredictionModel (run_id)"
    )
    
    # Disease Files fields - Crop and Location Information
    crop_name: str = Field(index=True, description="Name of the crop")
    image_path: str = Field(description="Path to the disease image")
    latitude: float = Field(description="GPS latitude coordinate")
    longitude: float = Field(description="GPS longitude coordinate")
    notes: str = Field(description="Additional notes about the disease file")
    
    # Disease Files fields - Environmental Conditions
    weather: WeatherCondition = Field(default=WeatherCondition.NORMAL, description="Weather condition")
    temperature: Optional[float] = Field(default=None, description="Temperature in Celsius")
    soil_moisture: Optional[float] = Field(default=None, description="Soil moisture percentage (0-100)")
    soil_temperature: Optional[float] = Field(default=None, description="Soil temperature in Celsius")
    soil_ph: Optional[float] = Field(default=None, description="Soil pH value (0-14)")
    uv_index: Optional[float] = Field(default=None, description="UV index value")
    
    # Disease Prediction fields - Disease Information
    disease_name: str = Field(index=True, description="Name of the predicted disease")
    disease_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the disease"
    )
    
    # Disease Prediction fields - Model Performance Metrics
    accuracy: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Accuracy score (0.0 to 1.0)"
    )
    precision: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Precision score (0.0 to 1.0)"
    )
    recall: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Recall score (0.0 to 1.0)"
    )
    f_one_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="F1 score (0.0 to 1.0)"
    )
    
    # Disease Prediction fields - Severity Information
    severity_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Severity score (0.0 to 1.0)"
    )
    severity_value: Optional[SeverityLevel] = Field(
        default=None,
        description="Severity level classification"
    )
    
    # Disease Prediction fields - Treatment Information
    treatment: Optional[str] = Field(
        default=None,
        description="Recommended treatment for the disease"
    )
    
    # Timestamps
    file_upload_dt: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when disease file was uploaded"
    )
    prediction_run_dt: Optional[datetime] = Field(
        default=None,
        description="Timestamp when disease prediction was made"
    )
    kb_created_dt: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when knowledge base record was created"
    )
