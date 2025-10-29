"""
AI Assistant Service - Універсальний помічник для всіх каналів.
Працює з Atlas, Website Chat, Mobile App, API.

Модульна архітектура: працює незалежно від джерела запиту.
"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from .booking_orchestrator import BookingOrchestrator
from .intent_classifier import IntentClassifier
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


class AssistantService:
    """
    Універсальний AI асистент для CoreSync.
    
    Функціонал:
    1. Обробка запитів від різних джерел (Atlas, Web, Mobile)
    2. Створення бронювань з оплатою
    3. FAQ та інформація про сервіси
    4. Перевірка доступності
    5. Розрахунок цін (з membership знижками)
    6. Збір контактів для newsletters
    """
    
    def __init__(self):
        self.booking_orchestrator = BookingOrchestrator()
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.response_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Завантажує шаблони відповідей."""
        try:
            import os
            from django.conf import settings
            
            templates_path = os.path.join(
                settings.BASE_DIR, 
                'ai_agent', 
                'response_templates.json'
            )
            
            with open(templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return {}
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int] = None,
        source: str = 'web',  # 'web', 'mobile', 'atlas_phone', 'atlas_sms'
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Головний метод обробки повідомлення.
        
        Args:
            message: Текст повідомлення від користувача
            session_id: ID сесії розмови
            user_id: ID користувача (якщо є)
            source: Джерело запиту
            context: Додатковий контекст
        
        Returns:
            Dict: {
                'response': str,  # Текст відповіді
                'actions': List[Dict],  # Дії (показати кнопки, форми, тощо)
                'metadata': Dict,  # Додаткова інфа
                'requires_payment': bool,
                'booking_data': Dict (якщо створено бронювання)
            }
        """
        try:
            # Класифікуємо намір (intent)
            intent = await self.intent_classifier.classify(message, context)
            
            # Оновлюємо контекст розмови
            conversation_context = await self.context_manager.update_context(
                session_id=session_id,
                user_message=message,
                detected_intent=intent
            )
            
            # Обробляємо в залежності від наміру
            if intent['type'] == 'booking':
                return await self._handle_booking_intent(
                    message, session_id, user_id, intent, conversation_context
                )
            
            elif intent['type'] == 'pricing':
                return await self._handle_pricing_request(
                    message, user_id, intent, conversation_context
                )
            
            elif intent['type'] == 'availability':
                return await self._handle_availability_check(
                    message, intent, conversation_context
                )
            
            elif intent['type'] == 'service_info':
                return await self._handle_service_info(
                    message, intent
                )
            
            elif intent['type'] == 'membership':
                return await self._handle_membership_info(
                    message, user_id
                )
            
            elif intent['type'] == 'cancellation':
                return await self._handle_cancellation(
                    message, session_id, user_id
                )
            
            elif intent['type'] == 'help':
                return self._get_help_response()
            
            elif intent['type'] == 'greeting':
                return self._get_greeting_response()
            
            else:
                return self._get_fallback_response(message)
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._get_error_response()
    
    async def _handle_booking_intent(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int],
        intent: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Обробляє намір забронювати."""
        
        # Перевіряємо чи є всі необхідні дані
        required_data = ['service_id', 'date', 'time']
        missing_data = [d for d in required_data if d not in context]
        
        if missing_data:
            # Збираємо недостатні дані
            return await self._collect_booking_data(missing_data[0], context)
        
        # Всі дані є - створюємо бронювання
        try:
            # Формуємо datetime
            booking_datetime = datetime.combine(
                context['date'],
                context['time']
            )
            
            # Створюємо через orchestrator
            booking_result = await self.booking_orchestrator.create_booking(
                service_id=context['service_id'],
                user_id=user_id,
                booking_datetime=booking_datetime,
                addons=context.get('addons', []),
                special_requests=context.get('special_requests'),
                conversation_session_id=session_id
            )
            
            # Формуємо відповідь
            response_text = f"""
✅ **Бронювання створено!**

📋 Референс: {booking_result['booking_reference']}
💰 До оплати: ${booking_result['total_price']} USD
👤 Майстер: {booking_result.get('technician', 'Буде призначено')}

Зараз перейдемо до оплати...
"""
            
            return {
                'response': response_text,
                'actions': [
                    {
                        'type': 'payment_required',
                        'booking_id': booking_result['booking_id'],
                        'amount': booking_result['total_price']
                    },
                    {
                        'type': 'show_payment_form',
                        'stripe_publishable_key': self._get_stripe_key()
                    }
                ],
                'metadata': {
                    'booking_id': booking_result['booking_id'],
                    'status': booking_result['status']
                },
                'requires_payment': True,
                'booking_data': booking_result
            }
        
        except Exception as e:
            logger.error(f"Booking creation failed: {str(e)}")
            return {
                'response': f"❌ Помилка при створенні бронювання: {str(e)}",
                'actions': [],
                'metadata': {'error': str(e)},
                'requires_payment': False
            }
    
    async def _collect_booking_data(
        self,
        missing_field: str,
        current_context: Dict
    ) -> Dict[str, Any]:
        """Збирає недостатні дані для бронювання."""
        
        if missing_field == 'service_id':
            return {
                'response': self.response_templates['booking_intent']['responses'][0],
                'actions': [
                    {
                        'type': 'show_service_options',
                        'options': self.response_templates['booking_intent']['options']
                    }
                ],
                'metadata': {'awaiting': 'service_selection'},
                'requires_payment': False
            }
        
        elif missing_field == 'date':
            return {
                'response': "На яку дату бажаєте забронювати?",
                'actions': [
                    {
                        'type': 'show_calendar',
                        'min_date': self._get_min_booking_date(),
                        'max_date': self._get_max_booking_date()
                    }
                ],
                'metadata': {'awaiting': 'date_selection'},
                'requires_payment': False
            }
        
        elif missing_field == 'time':
            # Перевіряємо доступність
            availability = await self.booking_orchestrator.check_availability(
                service_id=current_context['service_id'],
                preferred_date=current_context['date'],
                duration_minutes=60  # Default
            )
            
            return {
                'response': "Оберіть зручний час:",
                'actions': [
                    {
                        'type': 'show_time_slots',
                        'available_slots': [
                            slot.strftime('%H:%M') 
                            for slot in availability['suggested_slots']
                        ]
                    }
                ],
                'metadata': {'awaiting': 'time_selection'},
                'requires_payment': False
            }
        
        return self._get_fallback_response("")
    
    async def _handle_pricing_request(
        self,
        message: str,
        user_id: Optional[int],
        intent: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Обробляє запит про ціни."""
        
        service_type = intent.get('service_type')
        
        if not service_type:
            # Запитуємо про який сервіс
            return {
                'response': self.response_templates['pricing_request']['responses'][0],
                'actions': [
                    {
                        'type': 'show_service_categories',
                        'categories': ['massage', 'facial', 'barber', 'mani_pedi', 'private']
                    }
                ],
                'metadata': {'awaiting': 'service_type_for_pricing'},
                'requires_payment': False
            }
        
        # Отримуємо ціни для конкретного сервісу
        pricing = await self._get_service_pricing(service_type, user_id)
        
        response_text = f"""
💰 **Ціни на {service_type}:**

{pricing['formatted_text']}

{pricing['membership_note']}
"""
        
        return {
            'response': response_text,
            'actions': [
                {
                    'type': 'suggest_booking',
                    'service_type': service_type
                }
            ],
            'metadata': {'pricing_shown': True},
            'requires_payment': False
        }
    
    async def _handle_availability_check(
        self,
        message: str,
        intent: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Перевіряє доступність."""
        
        # Парсимо дату з message або context
        service_id = context.get('service_id') or intent.get('service_id')
        preferred_date = context.get('date') or intent.get('date')
        
        if not service_id or not preferred_date:
            return {
                'response': "Для якого сервісу та на яку дату хочете перевірити доступність?",
                'actions': [],
                'metadata': {},
                'requires_payment': False
            }
        
        # Перевіряємо через orchestrator
        availability = await self.booking_orchestrator.check_availability(
            service_id=service_id,
            preferred_date=preferred_date,
            duration_minutes=60
        )
        
        if availability['available']:
            response_text = f"✅ Доступно на {preferred_date.strftime('%d.%m.%Y')}!"
        else:
            response_text = f"❌ На жаль, зайнято. Альтернативні слоти:"
        
        return {
            'response': response_text,
            'actions': [
                {
                    'type': 'show_available_slots',
                    'slots': [
                        slot.strftime('%d.%m.%Y %H:%M')
                        for slot in availability['suggested_slots']
                    ]
                }
            ],
            'metadata': {'availability_checked': True},
            'requires_payment': False
        }
    
    async def _handle_service_info(
        self,
        message: str,
        intent: Dict
    ) -> Dict[str, Any]:
        """Надає інформацію про сервіси."""
        
        service_type = intent.get('service_type', 'general')
        
        templates = self.response_templates.get('service_info', {})
        info_text = templates.get(service_type, templates.get('massage', ''))
        
        return {
            'response': info_text,
            'actions': [
                {
                    'type': 'suggest_booking',
                    'service_type': service_type
                }
            ],
            'metadata': {'info_provided': service_type},
            'requires_payment': False
        }
    
    async def _handle_membership_info(
        self,
        message: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Інформація про membership."""
        
        response_text = self.response_templates['membership']['responses'][0]
        
        # Якщо користувач залогінений, додаємо персоналізовану інфу
        if user_id:
            from memberships.models import Membership
            from asgiref.sync import sync_to_async
            
            membership = await sync_to_async(
                lambda: Membership.objects.filter(
                    user_id=user_id, 
                    status='active'
                ).first()
            )()
            
            if membership:
                response_text += f"\n\n✨ У вас активний тариф: **{membership.tier.upper()}**"
        
        return {
            'response': response_text,
            'actions': [
                {
                    'type': 'show_membership_comparison',
                    'tiers': ['base', 'premium', 'unlimited']
                }
            ],
            'metadata': {'membership_info_shown': True},
            'requires_payment': False
        }
    
    async def _handle_cancellation(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Обробляє скасування бронювання."""
        
        if not user_id:
            return {
                'response': "Для скасування бронювання потрібно увійти в аккаунт.",
                'actions': [{'type': 'show_login_form'}],
                'metadata': {},
                'requires_payment': False
            }
        
        # Знаходимо активні бронювання користувача
        from services.models import Booking
        from asgiref.sync import sync_to_async
        
        bookings = await sync_to_async(
            lambda: list(Booking.objects.filter(
                user_id=user_id,
                status__in=['confirmed', 'pending']
            ).order_by('-booking_date'))
        )()
        
        if not bookings:
            return {
                'response': "У вас немає активних бронювань.",
                'actions': [],
                'metadata': {},
                'requires_payment': False
            }
        
        return {
            'response': "Оберіть бронювання для скасування:",
            'actions': [
                {
                    'type': 'show_booking_list',
                    'bookings': [
                        {
                            'id': b.id,
                            'service': b.service.name,
                            'date': b.booking_date.strftime('%d.%m.%Y'),
                            'time': b.booking_time.strftime('%H:%M')
                        }
                        for b in bookings
                    ]
                }
            ],
            'metadata': {'cancellation_mode': True},
            'requires_payment': False
        }
    
    def _get_greeting_response(self) -> Dict[str, Any]:
        """Вітальна відповідь."""
        import random
        
        responses = self.response_templates.get('greeting', {}).get('responses', [])
        follow_up = self.response_templates.get('greeting', {}).get('follow_up', '')
        
        response = random.choice(responses) if responses else "Вітаю!"
        
        return {
            'response': f"{response}\n\n{follow_up}",
            'actions': [
                {
                    'type': 'show_quick_actions',
                    'actions': [
                        'Забронювати',
                        'Ціни',
                        'Membership',
                        'Контакти'
                    ]
                }
            ],
            'metadata': {'greeting': True},
            'requires_payment': False
        }
    
    def _get_help_response(self) -> Dict[str, Any]:
        """Допомога."""
        response = self.response_templates.get('help', {}).get('responses', [''])[0]
        
        return {
            'response': response,
            'actions': [],
            'metadata': {'help_shown': True},
            'requires_payment': False
        }
    
    def _get_fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback коли не зрозуміли."""
        import random
        
        responses = self.response_templates.get('fallback', {}).get('responses', [])
        suggestions = self.response_templates.get('fallback', {}).get('suggestions', [])
        
        response = random.choice(responses) if responses else "Не зрозумів запит."
        suggestion = random.choice(suggestions) if suggestions else ""
        
        return {
            'response': f"{response}\n\n{suggestion}",
            'actions': [
                {
                    'type': 'show_suggestions',
                    'suggestions': ['Бронювання', 'Ціни', 'Сервіси']
                }
            ],
            'metadata': {'fallback': True},
            'requires_payment': False
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Відповідь при помилці."""
        import random
        
        responses = self.response_templates.get('error', {}).get('responses', [])
        response = random.choice(responses) if responses else "Технічна помилка."
        
        return {
            'response': response,
            'actions': [],
            'metadata': {'error': True},
            'requires_payment': False
        }
    
    async def _get_service_pricing(
        self,
        service_type: str,
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Отримує ціни для сервісу."""
        # TODO: Реальна логіка з БД
        
        # Placeholder
        pricing_text = f"Ціни залежать від membership. Базова ціна: $150-300."
        membership_note = "💡 З membership знижка до 40%!"
        
        return {
            'formatted_text': pricing_text,
            'membership_note': membership_note
        }
    
    def _get_min_booking_date(self) -> str:
        """Мінімальна дата бронювання (сьогодні)."""
        from django.utils import timezone
        return timezone.now().date().isoformat()
    
    def _get_max_booking_date(self) -> str:
        """Максимальна дата бронювання (3 дні для non-members)."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Default: 90 днів (можна перевірити membership)
        return (timezone.now().date() + timedelta(days=90)).isoformat()
    
    def _get_stripe_key(self) -> str:
        """Отримує Stripe publishable key."""
        from django.conf import settings
        return getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')


# Global instance
assistant_service = AssistantService()

