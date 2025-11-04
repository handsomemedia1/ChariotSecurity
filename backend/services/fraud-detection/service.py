from web3 import Web3
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

from .models import TransactionAnalysis, MaliciousContract, TokenApproval
from shared.config.settings import settings
from shared.utils.redis_client import redis_cache

logger = logging.getLogger(__name__)

class FraudDetectionService:
    def __init__(self):
        self.w3_ethereum = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
        self.w3_polygon = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        self.w3_bsc = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))
        
        self.chain_providers = {
            1: self.w3_ethereum,
            137: self.w3_polygon,
            56: self.w3_bsc
        }
    
    def get_provider(self, chain_id: int) -> Web3:
        '''Get Web3 provider for chain'''
        return self.chain_providers.get(chain_id, self.w3_ethereum)
    
    async def analyze_transaction(
        self,
        db: Session,
        user_id: str,
        to_address: str,
        data: str,
        value: str,
        chain_id: int
    ) -> Dict:
        '''Analyze transaction for threats'''
        logger.info(f'Analyzing transaction for user {user_id}')
        
        # Initialize risk factors
        risk_factors = []
        risk_score = 0.0
        threats = []
        
        # Check if contract is known malicious
        malicious = await self.check_malicious_contract(db, to_address, chain_id)
        if malicious:
            risk_score += 0.8
            risk_factors.append('known_malicious_contract')
            threats.append({
                'type': malicious['threat_type'],
                'severity': 'critical',
                'description': f'Contract is flagged as {malicious["threat_type"]}'
            })
        
        # Analyze contract code
        contract_risk = await self.analyze_contract_bytecode(to_address, chain_id)
        risk_score += contract_risk['score']
        if contract_risk['threats']:
            threats.extend(contract_risk['threats'])
            risk_factors.extend(contract_risk['factors'])
        
        # Simulate transaction
        simulation = await self.simulate_transaction(
            to_address, data, value, chain_id
        )
        if not simulation['success']:
            risk_score += 0.3
            risk_factors.append('simulation_failed')
            threats.append({
                'type': 'simulation_failure',
                'severity': 'high',
                'description': 'Transaction simulation failed'
            })
        
        # Check for suspicious patterns
        pattern_risk = await self.detect_suspicious_patterns(data)
        risk_score += pattern_risk['score']
        if pattern_risk['threats']:
            threats.extend(pattern_risk['threats'])
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Save analysis
        analysis = TransactionAnalysis(
            user_id=user_id,
            chain_id=chain_id,
            from_address='',  # Would come from user wallet
            to_address=to_address,
            value=value,
            risk_score=risk_score,
            simulation_result=simulation,
            threats_detected=threats
        )
        db.add(analysis)
        db.commit()
        
        return {
            'risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'threats': threats,
            'recommendation': self.get_recommendation(risk_score),
            'analysis_id': str(analysis.id),
            'simulation': simulation
        }
    
    async def check_malicious_contract(
        self,
        db: Session,
        address: str,
        chain_id: int
    ) -> Optional[Dict]:
        '''Check if contract is in malicious database'''
        # Check cache first
        cache_key = f'malicious:{chain_id}:{address.lower()}'
        cached = redis_cache.get(cache_key)
        if cached is not None:
            return cached if cached != 'safe' else None
        
        # Check database
        contract = db.query(MaliciousContract).filter(
            MaliciousContract.contract_address == address.lower(),
            MaliciousContract.chain_id == chain_id,
            MaliciousContract.is_active == True
        ).first()
        
        if contract:
            result = {
                'threat_type': contract.threat_type,
                'risk_score': contract.risk_score,
                'evidence': contract.evidence
            }
            redis_cache.set(cache_key, result, expire=3600)
            return result
        
        redis_cache.set(cache_key, 'safe', expire=3600)
        return None
    
    async def analyze_contract_bytecode(
        self,
        address: str,
        chain_id: int
    ) -> Dict:
        '''Analyze contract bytecode for malicious patterns'''
        w3 = self.get_provider(chain_id)
        
        try:
            bytecode = w3.eth.get_code(address).hex()
            
            if bytecode == '0x':
                return {'score': 0.0, 'threats': [], 'factors': []}
            
            threats = []
            factors = []
            score = 0.0
            
            # Check for dangerous opcodes
            dangerous_opcodes = ['selfdestruct', 'delegatecall']
            for opcode in dangerous_opcodes:
                if opcode in bytecode.lower():
                    score += 0.2
                    factors.append(f'contains_{opcode}')
                    threats.append({
                        'type': 'dangerous_opcode',
                        'severity': 'medium',
                        'description': f'Contract contains {opcode}'
                    })
            
            # Check contract age
            creation_block = await self.get_contract_creation_block(w3, address)
            if creation_block:
                current_block = w3.eth.block_number
                age_blocks = current_block - creation_block
                
                # Recently created contracts are riskier
                if age_blocks < 1000:  # Less than ~4 hours on Ethereum
                    score += 0.3
                    factors.append('newly_created')
                    threats.append({
                        'type': 'new_contract',
                        'severity': 'medium',
                        'description': 'Contract is newly created'
                    })
            
            return {'score': min(score, 1.0), 'threats': threats, 'factors': factors}
            
        except Exception as e:
            logger.error(f'Bytecode analysis error: {str(e)}')
            return {'score': 0.0, 'threats': [], 'factors': []}
    
    async def simulate_transaction(
        self,
        to_address: str,
        data: str,
        value: str,
        chain_id: int
    ) -> Dict:
        '''Simulate transaction execution'''
        w3 = self.get_provider(chain_id)
        
        try:
            # Use eth_call to simulate
            result = w3.eth.call({
                'to': to_address,
                'data': data,
                'value': int(value) if value else 0
            })
            
            return {
                'success': True,
                'result': result.hex(),
                'gas_estimate': 21000  # Simplified
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def detect_suspicious_patterns(self, data: str) -> Dict:
        '''Detect suspicious patterns in transaction data'''
        threats = []
        score = 0.0
        
        # Check for approval patterns
        # approve(address,uint256) = 0x095ea7b3
        if data.startswith('0x095ea7b3'):
            # Check if approval amount is max uint256 (unlimited)
            if 'f' * 60 in data.lower():
                score += 0.4
                threats.append({
                    'type': 'unlimited_approval',
                    'severity': 'high',
                    'description': 'Transaction requests unlimited token approval'
                })
        
        # Check for transferFrom patterns
        if '0x23b872dd' in data:
            score += 0.2
            threats.append({
                'type': 'transfer_from',
                'severity': 'medium',
                'description': 'Transaction uses transferFrom'
            })
        
        return {'score': min(score, 1.0), 'threats': threats}
    
    async def get_contract_creation_block(
        self,
        w3: Web3,
        address: str
    ) -> Optional[int]:
        '''Get block when contract was created'''
        try:
            # Binary search for creation block
            # Simplified implementation
            current_block = w3.eth.block_number
            
            # Check if contract exists
            code = w3.eth.get_code(address)
            if code == b'':
                return None
            
            # For simplicity, return a recent block
            # In production, implement proper binary search
            return current_block - 1000
            
        except Exception as e:
            logger.error(f'Error getting creation block: {str(e)}')
            return None
    
    def get_risk_level(self, score: float) -> str:
        '''Convert risk score to level'''
        if score >= 0.8:
            return 'Critical'
        elif score >= 0.6:
            return 'High'
        elif score >= 0.4:
            return 'Medium'
        elif score >= 0.2:
            return 'Low'
        return 'Safe'
    
    def get_recommendation(self, score: float) -> str:
        '''Get recommendation based on risk score'''
        if score >= 0.8:
            return '🚫 DO NOT PROCEED - High risk of loss'
        elif score >= 0.6:
            return '⚠️ PROCEED WITH EXTREME CAUTION'
        elif score >= 0.4:
            return '⚠️ Review carefully before proceeding'
        elif score >= 0.2:
            return '✓ Appears safe but verify details'
        return '✅ Transaction appears safe'
    
    async def report_malicious_contract(
        self,
        db: Session,
        address: str,
        chain_id: int,
        threat_type: str,
        evidence: Dict
    ):
        '''Report a malicious contract'''
        existing = db.query(MaliciousContract).filter(
            MaliciousContract.contract_address == address.lower(),
            MaliciousContract.chain_id == chain_id
        ).first()
        
        if existing:
            existing.last_updated = datetime.utcnow()
            existing.evidence = evidence
        else:
            contract = MaliciousContract(
                contract_address=address.lower(),
                chain_id=chain_id,
                threat_type=threat_type,
                risk_score=0.9,
                evidence=evidence
            )
            db.add(contract)
        
        db.commit()
        
        # Invalidate cache
        cache_key = f'malicious:{chain_id}:{address.lower()}'
        redis_cache.delete(cache_key)

fraud_detection_service = FraudDetectionService()
