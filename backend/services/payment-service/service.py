from web3 import Web3
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
import requests
import hashlib
import hmac

from .models import Subscription, Payment, CommissionEarning
from shared.config.settings import settings
from shared.utils.redis_client import redis_cache

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        # Initialize Web3 providers
        self.w3_ethereum = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
        self.w3_polygon = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        self.w3_bsc = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))
        
        self.chain_providers = {
            1: self.w3_ethereum,
            137: self.w3_polygon,
            56: self.w3_bsc
        }
        
        self.usdt_contracts = {
            1: settings.USDT_ETHEREUM,
            137: settings.USDT_POLYGON,
            56: settings.USDT_BSC
        }
        
        # Subscription plans
        self.plans = {
            'basic': {'price_usd': 9.99, 'price_ngn': 15000, 'duration_days': 30},
            'premium': {'price_usd': 29.99, 'price_ngn': 45000, 'duration_days': 30},
            'enterprise': {'price_usd': 99.99, 'price_ngn': 150000, 'duration_days': 30}
        }
    
    def get_provider(self, chain_id: int) -> Web3:
        '''Get Web3 provider for chain'''
        return self.chain_providers.get(chain_id, self.w3_ethereum)
    
    async def create_subscription(
        self,
        db: Session,
        user_id: str,
        plan_type: str,
        payment_method: str,
        currency: str = 'USD'
    ) -> Dict:
        '''Create a new subscription'''
        if plan_type not in self.plans:
            raise ValueError(f'Invalid plan type: {plan_type}')
        
        plan = self.plans[plan_type]
        amount = plan['price_usd'] if currency == 'USD' else plan['price_ngn']
        
        # Check for existing active subscription
        existing = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active'
        ).first()
        
        if existing:
            raise ValueError('User already has an active subscription')
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            amount=amount,
            currency=currency,
            status='pending'
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f'Subscription created: {subscription.id} for user {user_id}')
        
        return {
            'subscription_id': str(subscription.id),
            'plan_type': plan_type,
            'amount': amount,
            'currency': currency,
            'payment_instructions': await self.get_payment_instructions(
                payment_method, amount, currency, str(subscription.id)
            )
        }
    
    async def get_payment_instructions(
        self,
        payment_method: str,
        amount: float,
        currency: str,
        subscription_id: str
    ) -> Dict:
        '''Get payment instructions based on method'''
        if payment_method == 'usdt':
            return {
                'method': 'usdt',
                'instructions': 'Send USDT to the address below',
                'recipient_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',  # Your wallet
                'amount': amount,
                'supported_chains': [
                    {'chain_id': 1, 'name': 'Ethereum'},
                    {'chain_id': 137, 'name': 'Polygon'},
                    {'chain_id': 56, 'name': 'BSC'}
                ],
                'note': 'After payment, provide the transaction hash for verification'
            }
        elif payment_method == 'paystack':
            return await self.initialize_paystack_payment(amount, currency, subscription_id)
        else:
            raise ValueError(f'Unsupported payment method: {payment_method}')
    
    async def initialize_paystack_payment(
        self,
        amount: float,
        currency: str,
        subscription_id: str
    ) -> Dict:
        '''Initialize Paystack payment'''
        url = 'https://api.paystack.co/transaction/initialize'
        
        # Convert to kobo (Paystack uses smallest currency unit)
        amount_kobo = int(amount * 100)
        
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'amount': amount_kobo,
            'currency': 'NGN',
            'reference': f'CHR-{subscription_id}',
            'callback_url': f'{settings.CORS_ORIGINS[0]}/payment/verify'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data['status']:
                return {
                    'method': 'paystack',
                    'payment_url': data['data']['authorization_url'],
                    'reference': data['data']['reference'],
                    'access_code': data['data']['access_code']
                }
            else:
                raise Exception('Paystack initialization failed')
        
        except Exception as e:
            logger.error(f'Paystack initialization error: {str(e)}')
            raise ValueError('Failed to initialize payment')
    
    async def verify_usdt_payment(
        self,
        db: Session,
        subscription_id: str,
        transaction_hash: str,
        chain_id: int
    ) -> Dict:
        '''Verify USDT payment on blockchain'''
        logger.info(f'Verifying USDT payment: {transaction_hash} on chain {chain_id}')
        
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError('Subscription not found')
        
        # Get Web3 provider
        w3 = self.get_provider(chain_id)
        
        try:
            # Get transaction receipt
            receipt = w3.eth.get_transaction_receipt(transaction_hash)
            
            if not receipt or receipt['status'] != 1:
                raise ValueError('Transaction failed or not found')
            
            # Get transaction details
            tx = w3.eth.get_transaction(transaction_hash)
            
            # Verify it's a USDT transfer
            usdt_contract = self.usdt_contracts.get(chain_id)
            if tx['to'].lower() != usdt_contract.lower():
                raise ValueError('Transaction is not to USDT contract')
            
            # Decode transfer data
            # transfer(address,uint256) = 0xa9059cbb
            if not tx['input'].startswith('0xa9059cbb'):
                raise ValueError('Not a transfer transaction')
            
            # Extract recipient and amount
            input_data = tx['input'][10:]  # Remove function selector
            recipient = '0x' + input_data[24:64]
            amount_hex = input_data[64:128]
            amount_wei = int(amount_hex, 16)
            amount_usdt = amount_wei / 1e6  # USDT has 6 decimals
            
            # Verify recipient is your wallet
            expected_recipient = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'.lower()
            if recipient.lower() != expected_recipient:
                raise ValueError('Payment sent to wrong address')
            
            # Verify amount
            if amount_usdt < subscription.amount * 0.99:  # 1% tolerance
                raise ValueError(f'Insufficient payment amount: {amount_usdt} < {subscription.amount}')
            
            # Create payment record
            payment = Payment(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=amount_usdt,
                currency='USD',
                payment_method='usdt',
                transaction_hash=transaction_hash,
                chain_id=chain_id,
                status='completed',
                verified_at=datetime.utcnow()
            )
            db.add(payment)
            
            # Activate subscription
            subscription.status = 'active'
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(
                days=self.plans[subscription.plan_type]['duration_days']
            )
            
            # Handle community commission
            if subscription.user_id:
                await self.process_community_commission(db, payment)
            
            db.commit()
            
            logger.info(f'USDT payment verified: {transaction_hash}')
            
            return {
                'verified': True,
                'payment_id': str(payment.id),
                'subscription_status': 'active',
                'expires_at': subscription.current_period_end.isoformat()
            }
        
        except Exception as e:
            logger.error(f'USDT verification error: {str(e)}')
            raise ValueError(f'Payment verification failed: {str(e)}')
    
    async def verify_paystack_payment(
        self,
        db: Session,
        reference: str
    ) -> Dict:
        '''Verify Paystack payment'''
        url = f'https://api.paystack.co/transaction/verify/{reference}'
        
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data['status']:
                raise ValueError('Verification failed')
            
            tx_data = data['data']
            
            if tx_data['status'] != 'success':
                raise ValueError('Payment not successful')
            
            # Extract subscription_id from reference
            subscription_id = reference.replace('CHR-', '')
            
            # Get subscription
            subscription = db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise ValueError('Subscription not found')
            
            # Create payment record
            amount_ngn = tx_data['amount'] / 100  # Convert from kobo
            
            payment = Payment(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=amount_ngn,
                currency='NGN',
                payment_method='paystack',
                paystack_reference=reference,
                status='completed',
                verified_at=datetime.utcnow(),
                metadata=tx_data
            )
            db.add(payment)
            
            # Activate subscription
            subscription.status = 'active'
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(
                days=self.plans[subscription.plan_type]['duration_days']
            )
            
            # Handle community commission
            await self.process_community_commission(db, payment)
            
            db.commit()
            
            logger.info(f'Paystack payment verified: {reference}')
            
            return {
                'verified': True,
                'payment_id': str(payment.id),
                'subscription_status': 'active',
                'expires_at': subscription.current_period_end.isoformat()
            }
        
        except Exception as e:
            logger.error(f'Paystack verification error: {str(e)}')
            raise ValueError(f'Payment verification failed: {str(e)}')
    
    async def process_community_commission(
        self,
        db: Session,
        payment: Payment
    ):
        '''Process commission for community'''
        # Get user's community
        from services.auth_service.models import User
        
        user = db.query(User).filter(User.id == payment.user_id).first()
        
        if not user or not user.community_id:
            return
        
        # Check community member count
        from services.auth_service.models import Community
        community = db.query(Community).filter(
            Community.id == user.community_id
        ).first()
        
        if not community or community.member_count < 100:
            logger.info(f'Community {user.community_id} has less than 100 members, no commission')
            return
        
        # Calculate 5% commission
        commission_amount = payment.amount * 0.05
        
        # Create commission record
        commission = CommissionEarning(
            community_id=user.community_id,
            user_id=community.leader_id,
            amount=commission_amount,
            status='pending',
            period_start=datetime.utcnow().replace(day=1),
            period_end=(datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1)
        )
        db.add(commission)
        
        # Update community total
        community.total_commission += commission_amount
        
        # Update payment
        payment.community_id = user.community_id
        payment.commission_amount = commission_amount
        
        db.commit()
        
        logger.info(f'Commission processed: {commission_amount} for community {user.community_id}')
    
    async def get_user_subscription(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict]:
        '''Get user's active subscription'''
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active'
        ).first()
        
        if not subscription:
            return None
        
        return {
            'id': str(subscription.id),
            'plan_type': subscription.plan_type,
            'amount': subscription.amount,
            'currency': subscription.currency,
            'status': subscription.status,
            'current_period_start': subscription.current_period_start.isoformat(),
            'current_period_end': subscription.current_period_end.isoformat(),
            'auto_renew': subscription.auto_renew
        }
    
    async def cancel_subscription(
        self,
        db: Session,
        subscription_id: str,
        user_id: str
    ) -> bool:
        '''Cancel subscription'''
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == user_id
        ).first()
        
        if not subscription:
            return False
        
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        db.commit()
        
        logger.info(f'Subscription cancelled: {subscription_id}')
        return True
    
    async def get_community_earnings(
        self,
        db: Session,
        community_id: str
    ) -> Dict:
        '''Get community commission earnings'''
        earnings = db.query(CommissionEarning).filter(
            CommissionEarning.community_id == community_id
        ).all()
        
        total_earned = sum(e.amount for e in earnings)
        pending = sum(e.amount for e in earnings if e.status == 'pending')
        paid = sum(e.amount for e in earnings if e.status == 'paid')
        
        return {
            'total_earned': round(total_earned, 2),
            'pending': round(pending, 2),
            'paid': round(paid, 2),
            'earnings': [{
                'id': str(e.id),
                'amount': e.amount,
                'status': e.status,
                'period_start': e.period_start.isoformat(),
                'period_end': e.period_end.isoformat(),
                'created_at': e.created_at.isoformat()
            } for e in earnings]
        }

payment_service = PaymentService()
