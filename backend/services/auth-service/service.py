from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional, Dict
import secrets
import logging
from datetime import datetime

from .models import User, UserSession, Community
from shared.middleware.auth import create_access_token, create_refresh_token
from shared.utils.redis_client import redis_session

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    async def register_user(
        db: Session,
        email: str,
        password: str,
        device_fingerprint: Dict,
        wallet_address: Optional[str] = None,
        referral_code: Optional[str] = None
    ) -> Dict:
        '''Register new user'''
        # Check if email exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError('Email already registered')
        
        # Check if wallet exists
        if wallet_address:
            existing_wallet = db.query(User).filter(
                User.wallet_address == wallet_address
            ).first()
            if existing_wallet:
                raise ValueError('Wallet address already registered')
        
        # Handle referral code
        community_id = None
        if referral_code:
            community = db.query(Community).filter(
                Community.referral_code == referral_code
            ).first()
            if community:
                community_id = community.id
                community.member_count += 1
        
        # Create user
        user = User(
            email=email,
            password_hash=AuthService.hash_password(password),
            wallet_address=wallet_address,
            device_fingerprint=device_fingerprint,
            community_id=community_id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f'User registered: {user.id}')
        
        return {
            'user_id': str(user.id),
            'email': user.email,
            'wallet_address': user.wallet_address
        }
    
    @staticmethod
    async def login(
        db: Session,
        email: str,
        password: str,
        device_fingerprint: Dict,
        ip_address: str,
        user_agent: str
    ) -> Dict:
        '''User login'''
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user or not AuthService.verify_password(password, user.password_hash):
            raise ValueError('Invalid credentials')
        
        if not user.is_active:
            raise ValueError('Account is deactivated')
        
        # Check device fingerprint (single device enforcement)
        existing_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).all()
        
        if existing_sessions:
            # Deactivate old sessions
            for session in existing_sessions:
                session.is_active = False
        
        # Create new session
        session = UserSession(
            user_id=user.id,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(session)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        token_data = {'sub': str(user.id), 'email': user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store session in Redis
        redis_session.set(
            f'session:{user.id}',
            {'session_id': str(session.id), 'device': device_fingerprint},
            expire=86400 * 7  # 7 days
        )
        
        logger.info(f'User logged in: {user.id}')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'wallet_address': user.wallet_address,
                'subscription_tier': user.subscription_tier,
                'subscription_status': user.subscription_status
            }
        }
    
    @staticmethod
    async def logout(db: Session, user_id: str):
        '''User logout'''
        # Deactivate sessions
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({'is_active': False})
        db.commit()
        
        # Remove from Redis
        redis_session.delete(f'session:{user_id}')
        
        logger.info(f'User logged out: {user_id}')
    
    @staticmethod
    async def get_user_profile(db: Session, user_id: str) -> Dict:
        '''Get user profile'''
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError('User not found')
        
        return {
            'id': str(user.id),
            'email': user.email,
            'wallet_address': user.wallet_address,
            'subscription_tier': user.subscription_tier,
            'subscription_status': user.subscription_status,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    @staticmethod
    async def create_community(
        db: Session,
        user_id: str,
        community_name: str
    ) -> Dict:
        '''Create a new community'''
        # Check if user already leads a community
        existing = db.query(Community).filter(
            Community.leader_id == user_id
        ).first()
        if existing:
            raise ValueError('User already leads a community')
        
        # Generate unique referral code
        referral_code = f'CHR-{secrets.token_hex(4).upper()}'
        
        community = Community(
            name=community_name,
            leader_id=user_id,
            referral_code=referral_code
        )
        
        db.add(community)
        db.commit()
        db.refresh(community)
        
        logger.info(f'Community created: {community.id}')
        
        return {
            'id': str(community.id),
            'name': community.name,
            'referral_code': referral_code,
            'member_count': 0
        }

auth_service = AuthService()
