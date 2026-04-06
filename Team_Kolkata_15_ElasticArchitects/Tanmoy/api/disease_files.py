from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel
from model import DiseaseFilesModel, WeatherCondition, get_session

router = APIRouter(
    prefix="/api/disease-files",
    tags=["disease-files"],
)


# Pydantic models for request/response
class DiseaseFilesCreate(BaseModel):
    """Schema for creating disease files"""
    crop_name: str
    image_path: str
    latitude: float
    longitude: float
    notes: str
    weather: WeatherCondition = WeatherCondition.NORMAL
    temperature: float | None = None
    soil_moisture: float | None = None
    soil_temperature: float | None = None
    soil_ph: float | None = None
    uv_index: float | None = None


class DiseaseFilesRead(DiseaseFilesModel):
    """Schema for reading disease files"""
    pass


class DiseaseFilesUpdate(BaseModel):
    """Schema for updating disease files"""
    crop_name: str | None = None
    image_path: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    weather: WeatherCondition | None = None
    temperature: float | None = None
    soil_moisture: float | None = None
    soil_temperature: float | None = None
    soil_ph: float | None = None
    uv_index: float | None = None


# CREATE - Add a new disease file record
@router.post("/", response_model=DiseaseFilesRead, status_code=status.HTTP_201_CREATED)
def create_disease_file(
    disease_file: DiseaseFilesCreate,
    session: Session = Depends(get_session)
):
    """Create a new disease file record"""
    db_disease_file = DiseaseFilesModel.from_orm(disease_file)
    session.add(db_disease_file)
    session.commit()
    session.refresh(db_disease_file)
    return db_disease_file


# READ - Get all disease files
@router.get("/", response_model=list[DiseaseFilesRead])
def get_all_disease_files(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all disease file records with pagination"""
    disease_files = session.exec(
        select(DiseaseFilesModel).offset(skip).limit(limit)
    ).all()
    return disease_files


# READ - Get disease file by ID
@router.get("/{disease_file_id}", response_model=DiseaseFilesRead)
def get_disease_file(
    disease_file_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific disease file record by ID"""
    disease_file = session.get(DiseaseFilesModel, disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {disease_file_id} not found"
        )
    return disease_file


# READ - Get disease files by crop name
@router.get("/crop/{crop_name}", response_model=list[DiseaseFilesRead])
def get_disease_files_by_crop(
    crop_name: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease file records filtered by crop name"""
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.crop_name.ilike(f"%{crop_name}%"))
        .offset(skip)
        .limit(limit)
    ).all()
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found for crop: {crop_name}"
        )
    return disease_files


# READ - Get disease files by weather condition
@router.get("/weather/{weather_condition}", response_model=list[DiseaseFilesRead])
def get_disease_files_by_weather(
    weather_condition: WeatherCondition,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease file records filtered by weather condition"""
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.weather == weather_condition)
        .offset(skip)
        .limit(limit)
    ).all()
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found for weather: {weather_condition}"
        )
    return disease_files


# READ - Filter by temperature range
@router.get("/filter/temperature/{min_temp}/{max_temp}", response_model=list[DiseaseFilesRead])
def filter_by_temperature(
    min_temp: float,
    max_temp: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease files filtered by temperature range (in Celsius)"""
    if min_temp > max_temp:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_temp must be less than or equal to max_temp"
        )
    
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.temperature >= min_temp)
        .where(DiseaseFilesModel.temperature <= max_temp)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found with temperature between {min_temp}°C and {max_temp}°C"
        )
    return disease_files


# READ - Filter by soil moisture range
@router.get("/filter/soil-moisture/{min_moisture}/{max_moisture}", response_model=list[DiseaseFilesRead])
def filter_by_soil_moisture(
    min_moisture: float,
    max_moisture: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease files filtered by soil moisture range (0-100%)"""
    if not (0 <= min_moisture <= 100 and 0 <= max_moisture <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Soil moisture must be between 0 and 100"
        )
    
    if min_moisture > max_moisture:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_moisture must be less than or equal to max_moisture"
        )
    
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.soil_moisture >= min_moisture)
        .where(DiseaseFilesModel.soil_moisture <= max_moisture)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found with soil moisture between {min_moisture}% and {max_moisture}%"
        )
    return disease_files


# READ - Filter by soil temperature range
@router.get("/filter/soil-temperature/{min_soil_temp}/{max_soil_temp}", response_model=list[DiseaseFilesRead])
def filter_by_soil_temperature(
    min_soil_temp: float,
    max_soil_temp: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease files filtered by soil temperature range (in Celsius)"""
    if min_soil_temp > max_soil_temp:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_soil_temp must be less than or equal to max_soil_temp"
        )
    
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.soil_temperature >= min_soil_temp)
        .where(DiseaseFilesModel.soil_temperature <= max_soil_temp)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found with soil temperature between {min_soil_temp}°C and {max_soil_temp}°C"
        )
    return disease_files


# READ - Filter by soil pH range
@router.get("/filter/soil-ph/{min_ph}/{max_ph}", response_model=list[DiseaseFilesRead])
def filter_by_soil_ph(
    min_ph: float,
    max_ph: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease files filtered by soil pH range (0-14)"""
    if not (0 <= min_ph <= 14 and 0 <= max_ph <= 14):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Soil pH must be between 0 and 14"
        )
    
    if min_ph > max_ph:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_ph must be less than or equal to max_ph"
        )
    
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.soil_ph >= min_ph)
        .where(DiseaseFilesModel.soil_ph <= max_ph)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found with soil pH between {min_ph} and {max_ph}"
        )
    return disease_files


# READ - Filter by UV index range
@router.get("/filter/uv-index/{min_uv}/{max_uv}", response_model=list[DiseaseFilesRead])
def filter_by_uv_index(
    min_uv: float,
    max_uv: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease files filtered by UV index range"""
    if min_uv < 0 or max_uv < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="UV index cannot be negative"
        )
    
    if min_uv > max_uv:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_uv must be less than or equal to max_uv"
        )
    
    disease_files = session.exec(
        select(DiseaseFilesModel)
        .where(DiseaseFilesModel.uv_index >= min_uv)
        .where(DiseaseFilesModel.uv_index <= max_uv)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found with UV index between {min_uv} and {max_uv}"
        )
    return disease_files


# UPDATE - Update a disease file record
@router.put("/{disease_file_id}", response_model=DiseaseFilesRead)
def update_disease_file(
    disease_file_id: int,
    disease_file_update: DiseaseFilesUpdate,
    session: Session = Depends(get_session)
):
    """Update a disease file record"""
    disease_file = session.get(DiseaseFilesModel, disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {disease_file_id} not found"
        )
    
    update_data = disease_file_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(disease_file, key, value)
    
    session.add(disease_file)
    session.commit()
    session.refresh(disease_file)
    return disease_file


# DELETE - Delete a disease file record
@router.delete("/{disease_file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disease_file(
    disease_file_id: int,
    session: Session = Depends(get_session)
):
    """Delete a disease file record"""
    disease_file = session.get(DiseaseFilesModel, disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {disease_file_id} not found"
        )
    
    session.delete(disease_file)
    session.commit()
    return None


# DELETE - Delete all disease files for a specific crop
@router.delete("/crop/{crop_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disease_files_by_crop(
    crop_name: str,
    session: Session = Depends(get_session)
):
    """Delete all disease file records for a specific crop"""
    disease_files = session.exec(
        select(DiseaseFilesModel).where(DiseaseFilesModel.crop_name.ilike(f"%{crop_name}%"))
    ).all()
    
    if not disease_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No disease files found for crop: {crop_name}"
        )
    
    for disease_file in disease_files:
        session.delete(disease_file)
    session.commit()
    return None
