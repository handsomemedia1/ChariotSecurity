from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import reporting_service

router = APIRouter(prefix='/reports', tags=['Reporting'])

@router.get('/security')
async def generate_security_report(
    report_type: str = Query('weekly', regex='^(daily|weekly|monthly)$'),
    format: str = Query('json', regex='^(json|pdf)$'),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Generate security report'''
    try:
        report = await reporting_service.generate_security_report(
            db=db,
            user_id=current_user['sub'],
            report_type=report_type,
            format=format
        )
        return {'success': True, 'data': report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/compliance')
async def generate_compliance_report(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Generate compliance report'''
    try:
        report = await reporting_service.generate_compliance_report(
            db=db,
            user_id=current_user['sub']
        )
        return {'success': True, 'data': report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
