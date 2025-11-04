from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import json
import requests

from .models import SecurityEvent, AlertRule, Notification
from shared.config.settings import settings
from shared.utils.redis_client import redis_cache

logger = logging.getLogger(__name__)

class AlertEngineService:
    
    async def create_security_event(
        self,
        db: Session,
        user_id: str,
        event_type: str,
        severity: str,
        title: str,
        description: str = None,
        metadata: Dict = None
    ) -> Dict:
        '''Create a new security event'''
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            metadata=metadata or {}
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        logger.info(f'Security event created: {event.id} - {severity} - {event_type}')
        
        # Trigger notifications based on severity
        await self.process_event_notifications(db, event)
        
        # Send real-time alert via WebSocket (would integrate with WebSocket service)
        await self.send_realtime_alert(user_id, event)
        
        return {
            'id': str(event.id),
            'event_type': event.event_type,
            'severity': event.severity,
            'title': event.title,
            'created_at': event.created_at.isoformat()
        }
    
    async def process_event_notifications(
        self,
        db: Session,
        event: SecurityEvent
    ):
        '''Process notifications for an event'''
        # Determine notification channels based on severity
        channels = []
        
        if event.severity == 'critical':
            channels = ['push', 'email', 'sms']
        elif event.severity == 'high':
            channels = ['push', 'email']
        elif event.severity == 'medium':
            channels = ['push']
        else:
            channels = ['push']
        
        # Create notifications
        for channel in channels:
            notification = Notification(
                user_id=event.user_id,
                event_id=event.id,
                channel=channel,
                message=self.format_notification_message(event, channel)
            )
            db.add(notification)
        
        db.commit()
        
        # Send notifications asynchronously
        for channel in channels:
            await self.send_notification(
                user_id=str(event.user_id),
                channel=channel,
                message=self.format_notification_message(event, channel),
                event=event
            )
    
    def format_notification_message(
        self,
        event: SecurityEvent,
        channel: str
    ) -> str:
        '''Format notification message for different channels'''
        if channel == 'email':
            return f'''
            <html>
            <body>
            <h2>🚨 Security Alert: {event.title}</h2>
            <p><strong>Severity:</strong> {event.severity.upper()}</p>
            <p><strong>Type:</strong> {event.event_type}</p>
            <p><strong>Description:</strong> {event.description or 'N/A'}</p>
            <p><strong>Time:</strong> {event.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>Please review this alert in your Chariot Security dashboard.</p>
            </body>
            </html>
            '''
        elif channel == 'sms':
            return f'Chariot Security Alert ({event.severity}): {event.title}. Check your dashboard.'
        else:  # push, webhook
            return json.dumps({
                'title': event.title,
                'severity': event.severity,
                'type': event.event_type,
                'description': event.description,
                'timestamp': event.created_at.isoformat()
            })
    
    async def send_notification(
        self,
        user_id: str,
        channel: str,
        message: str,
        event: SecurityEvent
    ):
        '''Send notification via specified channel'''
        try:
            if channel == 'email':
                await self.send_email_notification(user_id, message, event)
            elif channel == 'sms':
                await self.send_sms_notification(user_id, message)
            elif channel == 'push':
                await self.send_push_notification(user_id, message)
            elif channel == 'webhook':
                await self.send_webhook_notification(user_id, message, event)
            
            logger.info(f'Notification sent via {channel} to user {user_id}')
        except Exception as e:
            logger.error(f'Failed to send {channel} notification: {str(e)}')
    
    async def send_email_notification(
        self,
        user_id: str,
        message: str,
        event: SecurityEvent
    ):
        '''Send email notification'''
        # In production, integrate with SendGrid, AWS SES, etc.
        logger.info(f'Email notification would be sent to user {user_id}')
        pass
    
    async def send_sms_notification(self, user_id: str, message: str):
        '''Send SMS notification'''
        # In production, integrate with Twilio, etc.
        logger.info(f'SMS notification would be sent to user {user_id}')
        pass
    
    async def send_push_notification(self, user_id: str, message: str):
        '''Send push notification'''
        # In production, integrate with FCM, APNS, etc.
        logger.info(f'Push notification would be sent to user {user_id}')
        pass
    
    async def send_webhook_notification(
        self,
        user_id: str,
        message: str,
        event: SecurityEvent
    ):
        '''Send webhook notification'''
        # Send to Slack, Discord, etc.
        if settings.SLACK_WEBHOOK_URL:
            try:
                payload = {
                    'text': f'🚨 *{event.title}*',
                    'attachments': [{
                        'color': self.get_severity_color(event.severity),
                        'fields': [
                            {'title': 'Severity', 'value': event.severity, 'short': True},
                            {'title': 'Type', 'value': event.event_type, 'short': True},
                            {'title': 'Description', 'value': event.description or 'N/A'}
                        ],
                        'footer': 'Chariot Security',
                        'ts': int(event.created_at.timestamp())
                    }]
                }
                requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
            except Exception as e:
                logger.error(f'Failed to send Slack notification: {str(e)}')
    
    def get_severity_color(self, severity: str) -> str:
        '''Get color code for severity'''
        colors = {
            'critical': '#ff0000',
            'high': '#ff6600',
            'medium': '#ffcc00',
            'low': '#0099ff'
        }
        return colors.get(severity, '#808080')
    
    async def send_realtime_alert(self, user_id: str, event: SecurityEvent):
        '''Send real-time alert via WebSocket'''
        # Store in Redis for WebSocket service to pick up
        alert_data = {
            'event_id': str(event.id),
            'user_id': user_id,
            'event_type': event.event_type,
            'severity': event.severity,
            'title': event.title,
            'description': event.description,
            'timestamp': event.created_at.isoformat()
        }
        
        redis_cache.set(
            f'realtime_alert:{user_id}:{event.id}',
            alert_data,
            expire=3600
        )
        
        # Publish to Redis pub/sub for WebSocket service
        # redis_pubsub.publish(f'user:{user_id}:alerts', json.dumps(alert_data))
    
    async def get_user_events(
        self,
        db: Session,
        user_id: str,
        limit: int = 50,
        severity: str = None,
        resolved: bool = None
    ) -> List[Dict]:
        '''Get security events for user'''
        query = db.query(SecurityEvent).filter(SecurityEvent.user_id == user_id)
        
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        
        if resolved is not None:
            query = query.filter(SecurityEvent.resolved == resolved)
        
        events = query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
        
        return [{
            'id': str(event.id),
            'event_type': event.event_type,
            'severity': event.severity,
            'title': event.title,
            'description': event.description,
            'metadata': event.metadata,
            'resolved': event.resolved,
            'created_at': event.created_at.isoformat()
        } for event in events]
    
    async def resolve_event(
        self,
        db: Session,
        event_id: str,
        user_id: str
    ) -> bool:
        '''Resolve a security event'''
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id,
            SecurityEvent.user_id == user_id
        ).first()
        
        if not event:
            return False
        
        event.resolved = True
        event.resolved_at = datetime.utcnow()
        db.commit()
        
        logger.info(f'Event resolved: {event_id}')
        return True
    
    async def get_alert_statistics(
        self,
        db: Session,
        user_id: str,
        days: int = 7
    ) -> Dict:
        '''Get alert statistics for user'''
        start_date = datetime.utcnow() - timedelta(days=days)
        
        events = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.created_at >= start_date
        ).all()
        
        stats = {
            'total_events': len(events),
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'resolved': 0,
            'unresolved': 0,
            'recent_threats': []
        }
        
        for event in events:
            stats['by_severity'][event.severity] += 1
            if event.resolved:
                stats['resolved'] += 1
            else:
                stats['unresolved'] += 1
        
        # Get recent unresolved threats
        recent = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.resolved == False
        ).order_by(SecurityEvent.created_at.desc()).limit(5).all()
        
        stats['recent_threats'] = [{
            'id': str(event.id),
            'title': event.title,
            'severity': event.severity,
            'created_at': event.created_at.isoformat()
        } for event in recent]
        
        return stats

alert_engine_service = AlertEngineService()
