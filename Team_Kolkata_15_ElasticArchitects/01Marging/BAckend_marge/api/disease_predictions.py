from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel
from dbhandler import get_db
from model import DiseasePredictionModel, DiseaseFilesModel, SeverityLevel, get_session
from repository.service import get_disease_service

router = APIRouter(
    prefix="/api/disease-predictions",
    tags=["disease-predictions"],
)

class DiseasePredictionCreateRequest(BaseModel):
    """Request model for creating prediction with LLM"""
    disease_file_id: int
    user_notes: Optional[str] = None

# Pydantic models for request/response
class DiseasePredictionCreate(BaseModel):
    """Schema for creating disease predictions"""
    disease_file_id: int
    disease_name: str | None = None
    accuracy: float
    precision: float
    recall: float
    f_one_score: float
    severity_score: float
    severity_value: SeverityLevel = SeverityLevel.NONE
    treatment: str


class DiseasePredictionRead(DiseasePredictionModel):
    """Schema for reading disease predictions"""
    pass


class DiseasePredictionUpdate(BaseModel):
    """Schema for updating disease predictions"""
    disease_file_id: int | None = None
    disease_name: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f_one_score: float | None = None
    severity_score: float | None = None
    severity_value: SeverityLevel | None = None
    treatment: str | None = None


# CREATE - Add a new disease prediction record
@router.post("/", response_model=DiseasePredictionRead, status_code=status.HTTP_201_CREATED)
async def create_disease_prediction(
    request: DiseasePredictionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new disease prediction using LLM analysis.
    
    This endpoint:
    1. Retrieves the disease file by ID
    2. Uses LLM to analyze the crop disease
    3. Generates predictions with metrics
    4. Stores the prediction in database
    """
    try:
        # Get disease file
        disease_file = db.query(DiseaseFilesModel).filter(
            DiseaseFilesModel.id == request.disease_file_id
        ).first()
        
        if not disease_file:
            raise HTTPException(
                status_code=404,
                detail=f"Disease file with ID {request.disease_file_id} not found"
            )
        
        # Get disease service
        disease_service = get_disease_service()
        
        # Combine notes
        combined_notes = disease_file.notes
        if request.user_notes:
            combined_notes += f"\n\nAdditional observations: {request.user_notes}"
        
        # Run LLM diagnosis
        print(f"Running LLM diagnosis for disease file {request.disease_file_id}...")
        diagnosis = await disease_service.diagnose_plant_disease(
            crop_name=disease_file.crop_name,
            image_path=disease_file.image_path,
            latitude=disease_file.latitude,
            longitude=disease_file.longitude,
            notes=combined_notes,
            weather=disease_file.weather.value if hasattr(disease_file.weather, 'value') else disease_file.weather,
            temperature=disease_file.temperature,
            soil_moisture=disease_file.soil_moisture,
            soil_temperature=disease_file.soil_temperature,
            soil_ph=disease_file.soil_ph,
            uv_index=disease_file.uv_index
        )
        
        print(f"✓ LLM diagnosis completed: {diagnosis['disease_name']}")
        
        # Create prediction record
        prediction = DiseasePredictionModel(
            disease_file_id=request.disease_file_id,
            disease_name=diagnosis['disease_name'],
            accuracy=diagnosis['accuracy'],
            precision=diagnosis['precision'],
            recall=diagnosis['recall'],
            f_one_score=diagnosis['f_one_score'],
            severity_score=diagnosis['severity_score'],
            severity_value=diagnosis['severity_level'],
            treatment=diagnosis['treatment']
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        print(f"✓ Prediction saved with run_id: {prediction.run_id}")
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create prediction: {str(e)}"
        )

# READ - Get all disease predictions
@router.get("/", response_model=list[DiseasePredictionRead])
def get_all_disease_predictions(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all disease prediction records with pagination"""
    predictions = session.exec(
        select(DiseasePredictionModel).offset(skip).limit(limit)
    ).all()
    return predictions


# READ - Get disease prediction by run ID
@router.get("/{run_id}", response_model=DiseasePredictionRead)
def get_disease_prediction(
    run_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific disease prediction record by run ID"""
    prediction = session.get(DiseasePredictionModel, run_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease prediction with run_id {run_id} not found"
        )
    return prediction


# READ - Get disease predictions by disease file ID
@router.get("/file/{disease_file_id}", response_model=list[DiseasePredictionRead])
def get_predictions_by_disease_file(
    disease_file_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all disease predictions for a specific disease file"""
    # Verify that the disease file exists
    disease_file = session.get(DiseaseFilesModel, disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {disease_file_id} not found"
        )
    
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.disease_file_id == disease_file_id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for disease file: {disease_file_id}"
        )
    return predictions


# READ - Get disease predictions by disease name
@router.get("/disease/{disease_name}", response_model=list[DiseasePredictionRead])
def get_predictions_by_disease_name(
    disease_name: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease prediction records filtered by disease name"""
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.disease_name.ilike(f"%{disease_name}%"))
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for disease: {disease_name}"
        )
    return predictions


# READ - Get predictions with accuracy above threshold
@router.get("/accuracy/{min_accuracy}", response_model=list[DiseasePredictionRead])
def get_predictions_by_accuracy(
    min_accuracy: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease predictions with accuracy above a minimum threshold"""
    if not 0.0 <= min_accuracy <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Accuracy must be between 0.0 and 1.0"
        )
    
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.accuracy >= min_accuracy)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found with accuracy >= {min_accuracy}"
        )
    return predictions


# READ - Filter by severity score range
@router.get("/filter/severity-score/{min_score}/{max_score}", response_model=list[DiseasePredictionRead])
def get_predictions_by_severity_score(
    min_score: float,
    max_score: float,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease predictions filtered by severity score range"""
    if not 0.0 <= min_score <= 1.0 or not 0.0 <= max_score <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Severity score must be between 0.0 and 1.0"
        )
    
    if min_score > max_score:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_score must be less than or equal to max_score"
        )
    
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.severity_score >= min_score)
        .where(DiseasePredictionModel.severity_score <= max_score)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found with severity score between {min_score} and {max_score}"
        )
    return predictions


# READ - Filter by severity level
@router.get("/filter/severity-level/{severity_level}", response_model=list[DiseasePredictionRead])
def get_predictions_by_severity_level(
    severity_level: SeverityLevel,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get disease predictions filtered by severity level"""
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.severity_value == severity_level)
        .offset(skip)
        .limit(limit)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found with severity level: {severity_level}"
        )
    return predictions


# UPDATE - Update a disease prediction record
@router.put("/{run_id}", response_model=DiseasePredictionRead)
def update_disease_prediction(
    run_id: int,
    prediction_update: DiseasePredictionUpdate,
    session: Session = Depends(get_session)
):
    """Update a disease prediction record"""
    prediction = session.get(DiseasePredictionModel, run_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease prediction with run_id {run_id} not found"
        )
    
    # If disease_file_id is being updated, verify it exists
    if prediction_update.disease_file_id and prediction_update.disease_file_id != prediction.disease_file_id:
        disease_file = session.get(DiseaseFilesModel, prediction_update.disease_file_id)
        if not disease_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease file with id {prediction_update.disease_file_id} not found"
            )
    
    update_data = prediction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(prediction, key, value)
    
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction


# DELETE - Delete a disease prediction record
@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disease_prediction(
    run_id: int,
    session: Session = Depends(get_session)
):
    """Delete a disease prediction record"""
    prediction = session.get(DiseasePredictionModel, run_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease prediction with run_id {run_id} not found"
        )
    
    session.delete(prediction)
    session.commit()
    return None


# DELETE - Delete all predictions for a specific disease file
@router.delete("/file/{disease_file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_predictions_by_disease_file(
    disease_file_id: int,
    session: Session = Depends(get_session)
):
    """Delete all predictions for a specific disease file"""
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.disease_file_id == disease_file_id)
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for disease file: {disease_file_id}"
        )
    
    for prediction in predictions:
        session.delete(prediction)
    session.commit()
    return None


# DELETE - Delete all predictions for a specific disease name
@router.delete("/disease/{disease_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_predictions_by_disease_name(
    disease_name: str,
    session: Session = Depends(get_session)
):
    """Delete all predictions for a specific disease name"""
    predictions = session.exec(
        select(DiseasePredictionModel)
        .where(DiseasePredictionModel.disease_name.ilike(f"%{disease_name}%"))
    ).all()
    
    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for disease: {disease_name}"
        )
    
    for prediction in predictions:
        session.delete(prediction)
    session.commit()
    return None
