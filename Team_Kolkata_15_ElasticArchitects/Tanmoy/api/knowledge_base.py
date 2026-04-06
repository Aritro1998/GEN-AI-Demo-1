from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel
from model import KnowledgeBaseModel, DiseaseFilesModel, SeverityLevel, get_session

router = APIRouter(
    prefix="/api/knowledge-base",
    tags=["knowledge-base"],
)


# Pydantic models for request/response
class KnowledgeBaseCreate(BaseModel):
    """Schema for creating knowledge base records"""
    disease_file_id: int
    disease_prediction_id: int | None = None
    crop_name: str
    image_path: str
    latitude: float
    longitude: float
    notes: str
    weather: str = "normal"
    temperature: float | None = None
    soil_moisture: float | None = None
    soil_temperature: float | None = None
    soil_ph: float | None = None
    uv_index: float | None = None
    disease_name: str
    disease_description: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f_one_score: float | None = None
    severity_score: float | None = None
    severity_value: SeverityLevel | None = None
    treatment: str | None = None
    prediction_run_dt: datetime | None = None


class KnowledgeBaseRead(KnowledgeBaseModel):
    """Schema for reading knowledge base records"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating knowledge base records"""
    disease_file_id: int | None = None
    disease_prediction_id: int | None = None
    crop_name: str | None = None
    image_path: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    weather: str | None = None
    temperature: float | None = None
    soil_moisture: float | None = None
    soil_temperature: float | None = None
    soil_ph: float | None = None
    uv_index: float | None = None
    disease_name: str | None = None
    disease_description: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f_one_score: float | None = None
    severity_score: float | None = None
    severity_value: SeverityLevel | None = None
    treatment: str | None = None
    prediction_run_dt: datetime | None = None


# CREATE - Add a new knowledge base record
@router.post("/", response_model=KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
def create_knowledge_base_record(
    kb_record: KnowledgeBaseCreate,
    session: Session = Depends(get_session)
):
    """Create a new knowledge base record combining disease file and prediction data"""
    # Verify that the disease file exists
    disease_file = session.get(DiseaseFilesModel, kb_record.disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {kb_record.disease_file_id} not found"
        )
    
    db_kb_record = KnowledgeBaseModel.from_orm(kb_record)
    session.add(db_kb_record)
    session.commit()
    session.refresh(db_kb_record)
    return db_kb_record


# READ - Get all knowledge base records
@router.get("/", response_model=list[KnowledgeBaseRead])
def get_all_knowledge_base_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all knowledge base records with pagination"""
    records = session.exec(
        select(KnowledgeBaseModel).offset(skip).limit(limit)
    ).all()
    return records


# READ - Get knowledge base record by ID
@router.get("/{kb_id}", response_model=KnowledgeBaseRead)
def get_knowledge_base_record(
    kb_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific knowledge base record by ID"""
    record = session.get(KnowledgeBaseModel, kb_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base record with id {kb_id} not found"
        )
    return record


# READ - Get records by crop name
@router.get("/crop/{crop_name}", response_model=list[KnowledgeBaseRead])
def get_by_crop_name(
    crop_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records filtered by crop name"""
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.crop_name.ilike(f"%{crop_name}%"))
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for crop: {crop_name}"
        )
    return records


# READ - Get records by disease name
@router.get("/disease/{disease_name}", response_model=list[KnowledgeBaseRead])
def get_by_disease_name(
    disease_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records filtered by disease name"""
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.disease_name.ilike(f"%{disease_name}%"))
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for disease: {disease_name}"
        )
    return records


# READ - Get records by severity level
@router.get("/severity/{severity_level}", response_model=list[KnowledgeBaseRead])
def get_by_severity_level(
    severity_level: SeverityLevel,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records filtered by severity level"""
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.severity_value == severity_level)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found with severity level: {severity_level}"
        )
    return records


# READ - Get records by disease file ID
@router.get("/file/{disease_file_id}", response_model=list[KnowledgeBaseRead])
def get_by_disease_file_id(
    disease_file_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records for a specific disease file"""
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.disease_file_id == disease_file_id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for disease file: {disease_file_id}"
        )
    return records


# READ - Get high accuracy records (predictions with accuracy above threshold)
@router.get("/filter/accuracy/{min_accuracy}", response_model=list[KnowledgeBaseRead])
def get_high_accuracy_records(
    min_accuracy: float,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records with prediction accuracy above threshold"""
    if not 0.0 <= min_accuracy <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Accuracy must be between 0.0 and 1.0"
        )
    
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.accuracy >= min_accuracy)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found with accuracy >= {min_accuracy}"
        )
    return records


# READ - Get records by location (latitude/longitude range)
@router.get("/location/{min_lat}/{max_lat}/{min_lon}/{max_lon}", response_model=list[KnowledgeBaseRead])
def get_by_location(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get knowledge base records filtered by geographical coordinates"""
    if min_lat > max_lat or min_lon > max_lon:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid coordinate range: min values must be less than max values"
        )
    
    records = session.exec(
        select(KnowledgeBaseModel)
        .where(KnowledgeBaseModel.latitude >= min_lat)
        .where(KnowledgeBaseModel.latitude <= max_lat)
        .where(KnowledgeBaseModel.longitude >= min_lon)
        .where(KnowledgeBaseModel.longitude <= max_lon)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found in the specified location range"
        )
    return records


# UPDATE - Update a knowledge base record
@router.put("/{kb_id}", response_model=KnowledgeBaseRead)
def update_knowledge_base_record(
    kb_id: int,
    kb_update: KnowledgeBaseUpdate,
    session: Session = Depends(get_session)
):
    """Update a knowledge base record"""
    record = session.get(KnowledgeBaseModel, kb_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base record with id {kb_id} not found"
        )
    
    # If disease_file_id is being updated, verify it exists
    if kb_update.disease_file_id and kb_update.disease_file_id != record.disease_file_id:
        disease_file = session.get(DiseaseFilesModel, kb_update.disease_file_id)
        if not disease_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease file with id {kb_update.disease_file_id} not found"
            )
    
    update_data = kb_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(record, key, value)
    
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


# DELETE - Delete a knowledge base record
@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base_record(
    kb_id: int,
    session: Session = Depends(get_session)
):
    """Delete a knowledge base record"""
    record = session.get(KnowledgeBaseModel, kb_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base record with id {kb_id} not found"
        )
    
    session.delete(record)
    session.commit()
    return None


# DELETE - Delete all records for a specific crop
@router.delete("/crop/{crop_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_by_crop_name(
    crop_name: str,
    session: Session = Depends(get_session)
):
    """Delete all knowledge base records for a specific crop"""
    records = session.exec(
        select(KnowledgeBaseModel).where(KnowledgeBaseModel.crop_name.ilike(f"%{crop_name}%"))
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for crop: {crop_name}"
        )
    
    for record in records:
        session.delete(record)
    session.commit()
    return None


# DELETE - Delete all records for a specific disease
@router.delete("/disease/{disease_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_by_disease_name(
    disease_name: str,
    session: Session = Depends(get_session)
):
    """Delete all knowledge base records for a specific disease"""
    records = session.exec(
        select(KnowledgeBaseModel).where(KnowledgeBaseModel.disease_name.ilike(f"%{disease_name}%"))
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for disease: {disease_name}"
        )
    
    for record in records:
        session.delete(record)
    session.commit()
    return None
