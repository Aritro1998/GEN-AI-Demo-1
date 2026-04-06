from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from model import DiseasePredictionModel, DiseaseFilesModel, get_session

router = APIRouter(
    prefix="/api/disease-predictions",
    tags=["disease-predictions"],
)


# Pydantic models for request/response
class DiseasePredictionCreate(DiseasePredictionModel):
    """Schema for creating disease predictions"""
    pass


class DiseasePredictionRead(DiseasePredictionModel):
    """Schema for reading disease predictions"""
    pass


class DiseasePredictionUpdate(DiseasePredictionModel):
    """Schema for updating disease predictions"""
    disease_file_id: int | None = None
    disease_name: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f_one_score: float | None = None


# CREATE - Add a new disease prediction record
@router.post("/", response_model=DiseasePredictionRead, status_code=status.HTTP_201_CREATED)
def create_disease_prediction(
    prediction: DiseasePredictionCreate,
    session: Session = Depends(get_session)
):
    """Create a new disease prediction record"""
    # Verify that the disease file exists
    disease_file = session.get(DiseaseFilesModel, prediction.disease_file_id)
    if not disease_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease file with id {prediction.disease_file_id} not found"
        )
    
    db_prediction = DiseasePredictionModel.from_orm(prediction)
    session.add(db_prediction)
    session.commit()
    session.refresh(db_prediction)
    return db_prediction


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
