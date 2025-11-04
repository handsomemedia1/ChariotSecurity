from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from shared.utils.database import get_db
from shared.middleware.auth import get_current_user
from .service import payment_service

router = APIRouter(prefix='/payment', tags=['Payment'])

class CreateSubscriptionRequest(BaseModel):
    plan_type: str
    payment_method: str
    currency: str = 'USD'

class VerifyUSDTRequest(BaseModel):
    subscription_id: str
    transaction_hash: str
    chain_id: int

class VerifyPaystackRequest(BaseModel):
    reference: str

@router.post('/subscription/create')
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Create new subscription'''
    try:
        result = await payment_service.create_subscription(
            db=db,
            user_id=current_user['sub'],
            plan_type=request.plan_type,
            payment_method=request.payment_method,
            currency=request.currency
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/verify/usdt')
async def verify_usdt(
    request: VerifyUSDTRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Verify USDT payment'''
    try:
        result = await payment_service.verify_usdt_payment(
            db=db,
            subscription_id=request.subscription_id,
            transaction_hash=request.transaction_hash,
            chain_id=request.chain_id
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/verify/paystack')
async def verify_paystack(
    request: VerifyPaystackRequest,
    db: Session = Depends(get_db)
):
    '''Verify Paystack payment'''
    try:
        result = await payment_service.verify_paystack_payment(
            db=db,
            reference=request.reference
        )
        return {'success': True, 'data': result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/subscription')
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Get user subscription'''
    subscription = await payment_service.get_user_subscription(
        db=db,
        user_id=current_user['sub']
    )
    return {'success': True, 'data': subscription}

@router.post('/subscription/{subscription_id}/cancel')
async def cancel_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Cancel subscription'''
    success = await payment_service.cancel_subscription(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user['sub']
    )
    
    if not success:
        raise HTTPException(status_code=404, detail='Subscription not found')
    
    return {'success': True, 'message': 'Subscription cancelled'}

@router.get('/community/{community_id}/earnings')
async def get_community_earnings(
    community_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Get community earnings'''
    earnings = await payment_service.get_community_earnings(
        db=db,
        community_id=community_id
    )
    return {'success': True, 'data': earnings}

@router.get('/plans')
async def get_plans():
    '''Get available subscription plans'''
    plans = [
        {
            'id': 'basic',
            'name': 'Basic',
            'price_usd': 9.99,
            'price_ngn': 15000,
            'features': [
                'Real-time threat detection',
                'Basic transaction analysis',
                '100 transactions/month',
                'Email alerts'
            ]
        },
        {
            'id': 'premium',
            'name': 'Premium',
            'price_usd': 29.99,
            'price_ngn': 45000,
            'features': [
                'Advanced ML threat detection',
                'Unlimited transaction analysis',
                'Priority alerts (Email, SMS, Push)',
                'Behavioral analysis',
                'API access'
            ]
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise',
            'price_usd': 99.99,
            'price_ngn': 150000,
            'features': [
                'All Premium features',
                'Custom ML models',
                'Dedicated support',
                'White-label options',
                'Custom integrations',
                'Advanced analytics'
            ]
        }
    ]
    return {'success': True, 'data': plans}
