from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import auth_service

router = APIRouter(prefix='/auth', tags=['Authentication'])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    wallet_address: Optional[str] = None
    referral_code: Optional[str] = None
    device_fingerprint: Dict

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: Dict

class CommunityRequest(BaseModel):
    name: str

@router.post('/register')
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    '''Register new user'''
    try:
        result = await auth_service.register_user(
            db=db,
            email=request.email,
            password=request.password,
            device_fingerprint=request.device_fingerprint,
            wallet_address=request.wallet_address,
            referral_code=request.referral_code
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/login')
async def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    '''User login'''
    try:
        result = await auth_service.login(
            db=db,
            email=request.email,
            password=request.password,
            device_fingerprint=request.device_fingerprint,
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get('user-agent', '')
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post('/logout')
async def logout(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''User logout'''
    await auth_service.logout(db, current_user['sub'])
    return {'success': True, 'message': 'Logged out successfully'}

@router.get('/me')
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Get current user profile'''
    try:
        profile = await auth_service.get_user_profile(db, current_user['sub'])
        return {'success': True, 'data': profile}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post('/community')
async def create_community(
    request: CommunityRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Create a community'''
    try:
        result = await auth_service.create_community(
            db=db,
            user_id=current_user['sub'],
            community_name=request.name
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
