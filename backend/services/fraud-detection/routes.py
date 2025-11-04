from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import fraud_detection_service

router = APIRouter(prefix='/fraud', tags=['Fraud Detection'])

class AnalyzeTransactionRequest(BaseModel):
    to_address: str
    data: str
    value: str
    chain_id: int

class ReportMaliciousRequest(BaseModel):
    address: str
    chain_id: int
    threat_type: str
    evidence: Dict

@router.post('/analyze')
async def analyze_transaction(
    request: AnalyzeTransactionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Analyze transaction for fraud'''
    try:
        result = await fraud_detection_service.analyze_transaction(
            db=db,
            user_id=current_user['sub'],
            to_address=request.to_address,
            data=request.data,
            value=request.value,
            chain_id=request.chain_id
        )
        return {'success': True, 'data': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/contract/{address}/{chain_id}')
async def check_contract(
    address: str,
    chain_id: int,
    db: Session = Depends(get_db)
):
    '''Check if contract is malicious'''
    result = await fraud_detection_service.check_malicious_contract(
        db, address, chain_id
    )
    
    if result:
        return {
            'success': True,
            'is_malicious': True,
            'data': result
        }
    
    return {
        'success': True,
        'is_malicious': False,
        'data': None
    }

@router.post('/report')
async def report_malicious(
    request: ReportMaliciousRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Report malicious contract'''
    try:
        await fraud_detection_service.report_malicious_contract(
            db=db,
            address=request.address,
            chain_id=request.chain_id,
            threat_type=request.threat_type,
            evidence=request.evidence
        )
        return {'success': True, 'message': 'Report submitted'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
