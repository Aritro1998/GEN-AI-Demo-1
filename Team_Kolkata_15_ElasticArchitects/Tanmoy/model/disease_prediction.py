from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import ForeignKey
from enum import Enum


class SeverityLevel(str, Enum):
    """Enum for disease severity levels"""
    NONE = "none"
    LOW = "low"
    AVERAGE = "average"
    HIGH = "high"


class DiseasePredictionModel(SQLModel, table=True):
    """Model for disease prediction results linked to disease files"""
    
    run_id: Optional[int] = Field(default=None, primary_key=True, description="Auto-incrementing primary key")
    disease_file_id: int = Field(
        foreign_key="diseasefilesmodel.id",
        description="Foreign key reference to DiseaseFilesModel"
    )
    disease_name: str = Field(index=True, description="Name of the predicted disease")
    accuracy: float = Field(ge=0.0, le=1.0, description="Accuracy score (0.0 to 1.0)")
    precision: float = Field(ge=0.0, le=1.0, description="Precision score (0.0 to 1.0)")
    recall: float = Field(ge=0.0, le=1.0, description="Recall score (0.0 to 1.0)")
    f_one_score: float = Field(ge=0.0, le=1.0, description="F1 score (0.0 to 1.0)")    
    severity_score: float = Field(ge=0.0, le=1.0, description="Severity score (0.0 to 1.0)")
    severity_value: SeverityLevel = Field(default=SeverityLevel.NONE, description="Severity level classification")
    treatment: str = Field(description="Recommended treatment for the disease")
    run_dt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of prediction run")
