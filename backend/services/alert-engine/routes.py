from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import alert_engine_service

router = APIRouter(prefix='/alerts', tags=['Alert Engine'])

class CreateEventRequest(BaseModel):
    event_type: str
    severity: str
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict] = None

@router.post('/event')
async def create_event(
    request: CreateEventRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Create security event'''
    try:
        result = await alert_engine_service.create_security_event(
            db=db,
            user_id=current_user['sub'],
            event_type=request.event_type,
            severity=request.severity,
            title=request.title,
            description=request.description,
            metadata=request.metadata
        )
        return {'success': True, 'data': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/events')
async def get_events(
    limit: int = Query(50, le=100),
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Get user security events'''
    events = await alert_engine_service.get_user_events(
        db=db,
        user_id=current_user['sub'],
        limit=limit,
        severity=severity,
        resolved=resolved
    )
    return {'success': True, 'data': events}

@router.post('/event/{event_id}/resolve')
async def resolve_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Resolve security event'''
    success = await alert_engine_service.resolve_event(
        db=db,
        event_id=event_id,
        user_id=current_user['sub']
    )
    
    if not success:
        raise HTTPException(status_code=404, detail='Event not found')
    
    return {'success': True, 'message': 'Event resolved'}

@router.get('/statistics')
async def get_statistics(
    days: int = Query(7, le=90),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Get alert statistics'''
    stats = await alert_engine_service.get_alert_statistics(
        db=db,
        user_id=current_user['sub'],
        days=days
    )
    return {'success': True, 'data': stats}
