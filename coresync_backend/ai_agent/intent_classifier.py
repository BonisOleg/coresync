"""
Intent Classifier - Detects user intent from messages.
Pattern-based matching (Phase 1), може бути розширено з spaCy/ML (Phase 2).
"""
import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies user intent з text messages.
    Uses pattern matching + keyword detection.
    """
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Load intent patterns (keywords, phrases).
        
        TODO: Phase 2 - move to database або JSON file.
        """
        return {
            'greeting': [
                r'\b(привіт|здрастуйте|добрий день|hello|hi)\b',
                r'\b(доброго ранку|доброго вечора)\b'
            ],
            'booking_intent': [
                r'\b(забронювати|бронювання|запис|book|appointment)\b',
                r'\b(хочу|потрібен|потребую)\b.*(масаж|facial|процедур)',
                r'\b(можна записатися|як записатися)\b'
            ],
            'pricing_request': [
                r'\b(ціна|скільки|вартість|price|cost)\b',
                r'\b(прайс|ціни|тариф)\b'
            ],
            'availability': [
                r'\b(вільні|доступні|available|free)\b.*(час|slot)',
                r'\b(коли можна|які дні)\b',
                r'\b(чи є місця|є вільні)\b'
            ],
            'membership': [
                r'\b(membership|членство|підписка)\b',
                r'\b(base|premium|unlimited)\b',
                r'\b(tier|план|пакет)\b'
            ],
            'service_info': [
                r'\b(що таке|розкажіть про|інформація про)\b',
                r'\b(опис|деталі|подробиці)\b.*(сервіс|процедур)'
            ],
            'payment': [
                r'\b(оплата|заплатити|pay|payment|card)\b',
                r'\b(картка|кредитна|stripe)\b'
            ],
            'cancellation': [
                r'\b(скасувати|відмінити|cancel)\b',
                r'\b(перенести|змінити час|reschedule)\b'
            ],
            'help': [
                r'\b(допомога|допоможіть|help)\b',
                r'\b(не розумію|не зрозумів|confused)\b'
            ]
        }
    
    async def classify(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify user message intent.
        
        Args:
            message: User message text
            context: Conversation context (для контекстного аналізу)
        
        Returns:
            Dict: {
                'type': intent_name,
                'confidence': float (0-1),
                'entities': extracted entities,
                'fallback': bool
            }
        """
        try:
            message_lower = message.lower()
            
            # Check patterns для кожного intent
            matches = []
            
            for intent_type, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message_lower, re.IGNORECASE):
                        matches.append((intent_type, self._calculate_confidence(pattern, message_lower)))
            
            # Sort by confidence
            matches.sort(key=lambda x: x[1], reverse=True)
            
            if matches:
                best_match = matches[0]
                return {
                    'type': best_match[0],
                    'confidence': best_match[1],
                    'entities': await self._extract_entities(message, best_match[0]),
                    'fallback': False,
                    'alternatives': [m[0] for m in matches[1:3]]  # Top 2 alternatives
                }
            else:
                # Fallback для unknown intents
                return {
                    'type': 'unknown',
                    'confidence': 0.0,
                    'entities': {},
                    'fallback': True,
                    'alternatives': []
                }
        
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return {
                'type': 'error',
                'confidence': 0.0,
                'entities': {},
                'fallback': True,
                'error': str(e)
            }
    
    def _calculate_confidence(self, pattern: str, message: str) -> float:
        """
        Calculate confidence score (simple heuristic).
        
        Phase 2: Replace з ML model confidence.
        """
        # Simple: count matches, normalize by message length
        matches = len(re.findall(pattern, message, re.IGNORECASE))
        message_words = len(message.split())
        
        if message_words == 0:
            return 0.0
        
        # Confidence = (matches / message_length) * boost_factor
        base_confidence = min(matches / message_words, 1.0)
        
        # Boost multi-word patterns
        pattern_words = len(pattern.split())
        boost = 1.0 + (pattern_words * 0.1)
        
        return min(base_confidence * boost, 1.0)
    
    async def _extract_entities(
        self, 
        message: str, 
        intent_type: str
    ) -> Dict[str, Any]:
        """
        Extract entities з message (dates, services, names).
        
        TODO: Phase 2 - use spaCy NER або custom extractors.
        """
        entities = {}
        
        # Service extraction
        service_patterns = {
            'massage': r'\b(масаж|massage|swedish|deep tissue|sports)\b',
            'facial': r'\b(фейшал|facial|gentlemans|executive)\b',
            'barber': r'\b(барбер|barber|стрижка|cut|shave)\b',
            'manicure': r'\b(манікюр|manicure|pedicure)\b'
        }
        
        for service, pattern in service_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                entities['service_type'] = service
                break
        
        # Date extraction (simple patterns)
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # DD/MM/YYYY
            r'\b(завтра|tomorrow|сьогодні|today)\b',
            r'\b(понеділок|вівторок|середа|thursday|friday)\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities['date_mention'] = match.group(0)
                break
        
        # Time extraction
        time_pattern = r'\b(\d{1,2}:\d{2}|\d{1,2}\s*(am|pm|AM|PM))\b'
        time_match = re.search(time_pattern, message)
        if time_match:
            entities['time_mention'] = time_match.group(0)
        
        return entities

