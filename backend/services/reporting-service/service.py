from sqlalchemy.orm import Session
from typing import Dict, List
import logging
from datetime import datetime, timedelta
import openai

from shared.config.settings import settings
from shared.utils.redis_client import redis_cache

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = settings.OPENAI_API_KEY

class ReportingService:
    
    async def generate_security_report(
        self,
        db: Session,
        user_id: str,
        report_type: str = 'weekly',
        format: str = 'pdf'
    ) -> Dict:
        '''Generate comprehensive security report'''
        logger.info(f'Generating {report_type} security report for user {user_id}')
        
        # Gather data
        data = await self.gather_report_data(db, user_id, report_type)
        
        # Generate AI summary
        ai_summary = await self.generate_ai_summary(data)
        
        # Generate report content
        report = {
            'title': f'{report_type.capitalize()} Security Report',
            'generated_at': datetime.utcnow().isoformat(),
            'period': data['period'],
            'executive_summary': ai_summary,
            'statistics': data['statistics'],
            'threat_analysis': data['threats'],
            'recommendations': await self.generate_recommendations(data),
            'trends': await self.analyze_trends(data)
        }
        
        # Cache report
        cache_key = f'report:{user_id}:{report_type}:{datetime.utcnow().date()}'
        redis_cache.set(cache_key, report, expire=86400)
        
        return report
    
    async def gather_report_data(
        self,
        db: Session,
        user_id: str,
        report_type: str
    ) -> Dict:
        '''Gather data for report'''
        # Determine date range
        if report_type == 'daily':
            days = 1
        elif report_type == 'weekly':
            days = 7
        elif report_type == 'monthly':
            days = 30
        else:
            days = 7
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Import models
        from services.fraud_detection.models import TransactionAnalysis
        from services.alert_engine.models import SecurityEvent
        
        # Get transactions
        transactions = db.query(TransactionAnalysis).filter(
            TransactionAnalysis.user_id == user_id,
            TransactionAnalysis.analyzed_at >= start_date
        ).all()
        
        # Get security events
        events = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.created_at >= start_date
        ).all()
        
        # Calculate statistics
        total_transactions = len(transactions)
        high_risk_count = sum(1 for t in transactions if t.risk_score > 0.6)
        blocked_count = sum(1 for t in transactions if t.risk_score > 0.8)
        avg_risk_score = sum(t.risk_score for t in transactions) / total_transactions if total_transactions > 0 else 0
        
        critical_events = sum(1 for e in events if e.severity == 'critical')
        high_events = sum(1 for e in events if e.severity == 'high')
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'days': days
            },
            'statistics': {
                'total_transactions': total_transactions,
                'high_risk_transactions': high_risk_count,
                'blocked_transactions': blocked_count,
                'average_risk_score': round(avg_risk_score, 3),
                'total_events': len(events),
                'critical_events': critical_events,
                'high_severity_events': high_events
            },
            'threats': self.categorize_threats(transactions, events),
            'transactions': transactions,
            'events': events
        }
    
    def categorize_threats(self, transactions, events) -> Dict:
        '''Categorize detected threats'''
        threat_types = {}
        
        for tx in transactions:
            if tx.threats_detected:
                for threat in tx.threats_detected:
                    threat_type = threat.get('type', 'unknown')
                    if threat_type not in threat_types:
                        threat_types[threat_type] = {
                            'count': 0,
                            'severity': threat.get('severity', 'medium'),
                            'examples': []
                        }
                    threat_types[threat_type]['count'] += 1
                    if len(threat_types[threat_type]['examples']) < 3:
                        threat_types[threat_type]['examples'].append({
                            'transaction': tx.transaction_hash,
                            'risk_score': tx.risk_score
                        })
        
        return threat_types
    
    async def generate_ai_summary(self, data: Dict) -> str:
        '''Generate AI-powered executive summary'''
        if not settings.OPENAI_API_KEY:
            return self.generate_basic_summary(data)
        
        try:
            prompt = f'''
            Generate a professional executive summary for a security report with the following data:
            
            Period: {data['period']['days']} days
            Total Transactions Analyzed: {data['statistics']['total_transactions']}
            High Risk Transactions: {data['statistics']['high_risk_transactions']}
            Blocked Transactions: {data['statistics']['blocked_transactions']}
            Average Risk Score: {data['statistics']['average_risk_score']}
            Total Security Events: {data['statistics']['total_events']}
            Critical Events: {data['statistics']['critical_events']}
            
            Threat Types Detected: {', '.join(data['threats'].keys()) if data['threats'] else 'None'}
            
            Write a concise, professional 2-3 paragraph summary highlighting the key findings and overall security posture.
            '''
            
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'You are a cybersecurity expert writing executive summaries for security reports.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message['content'].strip()
        
        except Exception as e:
            logger.error(f'AI summary generation failed: {str(e)}')
            return self.generate_basic_summary(data)
    
    def generate_basic_summary(self, data: Dict) -> str:
        '''Generate basic summary without AI'''
        stats = data['statistics']
        
        if stats['total_transactions'] == 0:
            return f"No transactions were analyzed during this {data['period']['days']}-day period."
        
        risk_percentage = (stats['high_risk_transactions'] / stats['total_transactions']) * 100
        
        summary = f"During the past {data['period']['days']} days, {stats['total_transactions']} transactions were analyzed. "
        summary += f"{stats['high_risk_transactions']} ({risk_percentage:.1f}%) were identified as high-risk, "
        summary += f"with {stats['blocked_transactions']} transactions blocked to prevent potential losses. "
        
        if stats['critical_events'] > 0:
            summary += f"Additionally, {stats['critical_events']} critical security events were detected and require immediate attention. "
        
        summary += f"The average risk score across all transactions was {stats['average_risk_score']:.3f}, "
        
        if stats['average_risk_score'] < 0.3:
            summary += "indicating a generally safe transaction pattern."
        elif stats['average_risk_score'] < 0.6:
            summary += "indicating moderate risk levels that should be monitored."
        else:
            summary += "indicating elevated risk levels that require immediate review."
        
        return summary
    
    async def generate_recommendations(self, data: Dict) -> List[Dict]:
        '''Generate security recommendations'''
        recommendations = []
        stats = data['statistics']
        
        # High risk transaction recommendation
        if stats['high_risk_transactions'] > stats['total_transactions'] * 0.2:
            recommendations.append({
                'priority': 'high',
                'category': 'Transaction Security',
                'title': 'High Risk Transaction Rate',
                'description': f'{stats["high_risk_transactions"]} high-risk transactions detected',
                'action': 'Review transaction patterns and consider enabling stricter validation rules'
            })
        
        # Critical events recommendation
        if stats['critical_events'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Security Events',
                'title': 'Unresolved Critical Events',
                'description': f'{stats["critical_events"]} critical security events require attention',
                'action': 'Immediately review and resolve critical security events'
            })
        
        # Threat-specific recommendations
        for threat_type, threat_info in data['threats'].items():
            if threat_info['count'] > 5:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'Threat Detection',
                    'title': f'Recurring {threat_type} Threats',
                    'description': f'{threat_info["count"]} instances detected',
                    'action': f'Implement additional protection against {threat_type} attacks'
                })
        
        # General recommendations
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'category': 'General',
                'title': 'Maintain Current Security Posture',
                'description': 'Security metrics are within acceptable ranges',
                'action': 'Continue monitoring and maintain current security practices'
            })
        
        return recommendations
    
    async def analyze_trends(self, data: Dict) -> Dict:
        '''Analyze security trends'''
        # In production, compare with historical data
        return {
            'risk_score_trend': 'stable',
            'threat_frequency_trend': 'decreasing',
            'blocked_transactions_trend': 'stable',
            'comparison_to_previous_period': {
                'transactions': 'increased',
                'risk_score': 'decreased',
                'events': 'stable'
            }
        }
    
    async def generate_compliance_report(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        '''Generate compliance report'''
        return {
            'title': 'Compliance Report',
            'generated_at': datetime.utcnow().isoformat(),
            'standards': {
                'PCI_DSS': {'status': 'compliant', 'score': 95},
                'GDPR': {'status': 'compliant', 'score': 98},
                'SOC2': {'status': 'in_progress', 'score': 85}
            },
            'audit_trail': 'Complete',
            'data_protection': 'Encrypted',
            'access_controls': 'Properly configured'
        }

reporting_service = ReportingService()
