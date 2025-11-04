from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import ml_serving_service

router = APIRouter(prefix='/ml', tags=['ML Serving'])

class FraudPredictionRequest(BaseModel):
    features: Dict

class AnomalyDetectionRequest(BaseModel):
    user_behavior: Dict

class RiskScoringRequest(BaseModel):
    risk_factors: Dict

@router.post('/predict/fraud')
async def predict_fraud(
    request: FraudPredictionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Predict fraud probability'''
    try:
        result = await ml_serving_service.predict_fraud(
            db=db,
            features=request.features,
            user_id=current_user['sub']
        )
        return {'success': True, 'data': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/predict/anomaly')
async def detect_anomaly(
    request: AnomalyDetectionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Detect behavioral anomalies'''
    try:
        result = await ml_serving_service.detect_anomaly(
            db=db,
            user_behavior=request.user_behavior,
            user_id=current_user['sub']
        )
        return {'success': True, 'data': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/predict/risk')
async def calculate_risk(
    request: RiskScoringRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Calculate risk score'''
    try:
        result = await ml_serving_service.calculate_risk_score(
            db=db,
            risk_factors=request.risk_factors,
            user_id=current_user['sub']
        )
        return {'success': True, 'data': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/models')
async def list_models():
    '''List available ML models'''
    models = [
        {
            'name': 'fraud_detection',
            'version': '1.0.0',
            'status': 'active',
            'accuracy': 0.94
        },
        {
            'name': 'anomaly_detection',
            'version': '1.0.0',
            'status': 'active',
            'accuracy': 0.89
        },
        {
            'name': 'risk_scoring',
            'version': '1.0.0',
            'status': 'active',
            'accuracy': 0.91
        }
    ]
    return {'success': True, 'data': models}
