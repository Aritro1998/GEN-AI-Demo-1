from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class WeatherCondition(str, Enum):
    """Enum for weather conditions"""
    HOT = "hot"
    COLD = "cold"
    NORMAL = "normal"
    FLOOD = "flood"


class DiseaseFilesModel(SQLModel, table=True):
    """Model for disease file records with location and weather information"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    crop_name: str = Field(index=True)
    image_path: str
    latitude: float
    longitude: float
    notes: str
    weather: WeatherCondition = Field(default=WeatherCondition.NORMAL)
    temperature: Optional[float] = Field(default=None, description="Temperature in Celsius")
    soil_moisture: Optional[float] = Field(default=None, description="Soil moisture percentage (0-100)")
    soil_temperature: Optional[float] = Field(default=None, description="Soil temperature in Celsius")
    soil_ph: Optional[float] = Field(default=None, description="Soil pH value (0-14)")
    uv_index: Optional[float] = Field(default=None, description="UV index value")
    upload_dt: datetime = Field(default_factory=datetime.utcnow)
