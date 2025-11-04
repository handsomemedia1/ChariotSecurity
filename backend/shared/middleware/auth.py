from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from shared.config.settings import settings
from shared.utils.redis_client import redis_session

logger = logging.getLogger(__name__)
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    '''Create JWT access token'''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire, 'type': 'access'})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict):
    '''Create JWT refresh token'''
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'type': 'refresh'})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    '''Verify and decode JWT token'''
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f'Token verification failed: {str(e)}')
        raise HTTPException(
            status_code=401,
            detail='Could not validate credentials'
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    '''Dependency to get current authenticated user'''
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')
    
    # Check if session is valid in Redis
    session_key = f'session:{user_id}'
    if not redis_session.exists(session_key):
        raise HTTPException(status_code=401, detail='Session expired')
    
    return payload

def verify_device_fingerprint(user_id: str, fingerprint: str) -> bool:
    '''Verify device fingerprint matches stored fingerprint'''
    stored_fingerprint = redis_session.get(f'device:{user_id}')
    return stored_fingerprint == fingerprint
