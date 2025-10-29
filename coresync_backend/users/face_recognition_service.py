"""
Face Recognition Service для CoreSync.
Гібридний сервіс: AWS Rekognition (primary) + Local fallback.
"""
import logging
import base64
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_provider():
    """Визначити який provider використовувати"""
    provider = settings.FACE_RECOGNITION_PROVIDER
    
    if provider == 'aws':
        try:
            from .aws_face_service import AWSFaceRecognition
            return AWSFaceRecognition()
        except Exception as e:
            logger.warning(f"AWS not available, falling back to local: {str(e)}")
            return None
    
    return None


class FaceRecognitionService:
    """
    Сервіс для розпізнавання облич.
    
    ВАЖЛИВО: Це placeholder implementation!
    Для production потрібна інтеграція з реальним face recognition API:
    - AWS Rekognition
    - Azure Face API
    - Google Cloud Vision
    - Або власна ML модель
    """
    
    SIMILARITY_THRESHOLD = 0.85  # 85% схожість для автентифікації
    MIN_FACE_DATA_SIZE = 100  # Мінімальний розмір даних
    
    @classmethod
    def register_face(
        cls,
        user,
        face_data: str,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Зареєструвати biometric template користувача.
        
        Args:
            user: User instance
            face_data: Base64 encoded face image або template
            metadata: Додаткові метадані (quality score, capture device, etc.)
        
        Returns:
            dict з результатом реєстрації
        """
        try:
            # Валідувати face_data
            validation_result = cls._validate_face_data(face_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # TODO: Тут буде виклик реального face recognition API
            # Наразі просто генеруємо placeholder template
            face_template = cls._generate_face_template(face_data, metadata)
            
            # Зберегти encrypted template
            encrypted_template = cls._encrypt_template(face_template)
            
            user.face_recognition_data = encrypted_template
            user.biometric_enabled = True
            user.save()
            
            logger.info(f"Face registered for user {user.id}")
            
            return {
                'success': True,
                'message': 'Face registered successfully',
                'template_id': cls._generate_template_id(user.id),
                'registered_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error registering face: {str(e)}")
            return {
                'success': False,
                'error': f'Registration failed: {str(e)}'
            }
    
    @classmethod
    def verify_face(
        cls,
        user,
        face_data: str
    ) -> Dict[str, Any]:
        """
        Перевірити чи відповідає face_data збереженому template.
        
        Args:
            user: User instance
            face_data: Base64 encoded face image для перевірки
        
        Returns:
            dict з результатом верифікації
        """
        try:
            # Перевірити чи є збережений template
            if not user.face_recognition_data or not user.biometric_enabled:
                return {
                    'success': False,
                    'verified': False,
                    'error': 'No biometric data registered'
                }
            
            # Валідувати вхідні дані
            validation_result = cls._validate_face_data(face_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'verified': False,
                    'error': validation_result['error']
                }
            
            # TODO: Тут буде виклик реального face recognition API
            # Наразі placeholder порівняння
            stored_template = cls._decrypt_template(user.face_recognition_data)
            current_template = cls._generate_face_template(face_data)
            
            similarity = cls._compare_templates(stored_template, current_template)
            verified = similarity >= cls.SIMILARITY_THRESHOLD
            
            logger.info(f"Face verification for user {user.id}: {verified} (similarity: {similarity})")
            
            return {
                'success': True,
                'verified': verified,
                'similarity': round(similarity, 3),
                'threshold': cls.SIMILARITY_THRESHOLD,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error verifying face: {str(e)}")
            return {
                'success': False,
                'verified': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    @classmethod
    def authenticate_face(
        cls,
        face_data: str
    ) -> Dict[str, Any]:
        """
        Автентифікувати користувача за обличчям.
        Знайти користувача в базі з matching face template.
        
        Args:
            face_data: Base64 encoded face image
        
        Returns:
            dict з результатом автентифікації та user_id якщо знайдено
        """
        try:
            from .models import User
            
            # Валідувати face_data
            validation_result = cls._validate_face_data(face_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'authenticated': False,
                    'error': validation_result['error']
                }
            
            # TODO: Тут буде пошук користувача через face recognition API
            # Наразі placeholder - шукаємо серед активних користувачів
            current_template = cls._generate_face_template(face_data)
            
            active_users = User.objects.filter(
                biometric_enabled=True,
                is_active=True
            ).exclude(face_recognition_data='')
            
            best_match = None
            best_similarity = 0
            
            for user in active_users:
                stored_template = cls._decrypt_template(user.face_recognition_data)
                similarity = cls._compare_templates(stored_template, current_template)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user
            
            if best_match and best_similarity >= cls.SIMILARITY_THRESHOLD:
                logger.info(f"Face authentication successful: user {best_match.id}")
                
                return {
                    'success': True,
                    'authenticated': True,
                    'user_id': best_match.id,
                    'email': best_match.email,
                    'similarity': round(best_similarity, 3),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Face authentication failed: no match found (best: {best_similarity})")
                
                return {
                    'success': True,
                    'authenticated': False,
                    'message': 'No matching face found',
                    'best_similarity': round(best_similarity, 3) if best_similarity > 0 else None
                }
        
        except Exception as e:
            logger.error(f"Error authenticating face: {str(e)}")
            return {
                'success': False,
                'authenticated': False,
                'error': f'Authentication failed: {str(e)}'
            }
    
    @classmethod
    def delete_face_data(cls, user) -> Dict[str, Any]:
        """Видалити biometric дані користувача"""
        try:
            user.face_recognition_data = None
            user.biometric_enabled = False
            user.save()
            
            logger.info(f"Face data deleted for user {user.id}")
            
            return {
                'success': True,
                'message': 'Biometric data deleted successfully'
            }
        
        except Exception as e:
            logger.error(f"Error deleting face data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # === Helper Methods (PLACEHOLDER IMPLEMENTATIONS) ===
    
    @staticmethod
    def _validate_face_data(face_data: str) -> Dict:
        """Валідувати face data"""
        if not face_data:
            return {'valid': False, 'error': 'Face data is empty'}
        
        if len(face_data) < FaceRecognitionService.MIN_FACE_DATA_SIZE:
            return {'valid': False, 'error': 'Face data too small'}
        
        # Перевірити чи це валідний base64
        try:
            base64.b64decode(face_data)
        except Exception:
            return {'valid': False, 'error': 'Invalid base64 format'}
        
        return {'valid': True}
    
    @staticmethod
    def _generate_face_template(face_data: str, metadata: Dict = None) -> str:
        """
        Генерувати face template з image data.
        PLACEHOLDER - в production тут буде ML модель.
        """
        # Наразі просто хешуємо дані
        face_hash = hashlib.sha256(face_data.encode()).hexdigest()
        
        template = {
            'version': '1.0',
            'hash': face_hash,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        return json.dumps(template)
    
    @staticmethod
    def _encrypt_template(template: str) -> str:
        """
        Зашифрувати template для зберігання.
        PLACEHOLDER - в production використовувати реальне шифрування.
        """
        # Наразі просто base64 encode
        return base64.b64encode(template.encode()).decode()
    
    @staticmethod
    def _decrypt_template(encrypted_template: str) -> str:
        """
        Розшифрувати template.
        PLACEHOLDER - в production використовувати реальне шифрування.
        """
        try:
            return base64.b64decode(encrypted_template.encode()).decode()
        except Exception:
            return '{}'
    
    @staticmethod
    def _compare_templates(template1: str, template2: str) -> float:
        """
        Порівняти два face templates.
        PLACEHOLDER - в production використовувати реальний face matching algorithm.
        
        Returns:
            float: similarity score від 0.0 до 1.0
        """
        try:
            t1 = json.loads(template1)
            t2 = json.loads(template2)
            
            # Наразі просто порівнюємо хеші
            if t1.get('hash') == t2.get('hash'):
                return 0.95  # Точне співпадіння
            else:
                # Placeholder: випадкова схожість 0.3-0.7
                import random
                return random.uniform(0.3, 0.7)
        
        except Exception:
            return 0.0
    
    @staticmethod
    def _generate_template_id(user_id: int) -> str:
        """Генерувати unique ID для template"""
        timestamp = datetime.now().timestamp()
        data = f"{user_id}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


# Convenience functions для використання в views

def register_user_face(user, face_data: str, metadata: Dict = None) -> Dict:
    """
    Wrapper function для реєстрації.
    Спробує AWS спочатку, fallback до local.
    """
    # Спробувати AWS
    if settings.FACE_RECOGNITION_PROVIDER == 'aws':
        try:
            from .aws_face_service import register_face_aws
            result = register_face_aws(user, face_data)
            
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"AWS registration failed, trying local: {str(e)}")
    
    # Fallback до local
    return FaceRecognitionService.register_face(user, face_data, metadata)


def verify_user_face(user, face_data: str) -> Dict:
    """
    Wrapper function для верифікації.
    Спробує AWS спочатку, fallback до local.
    """
    if settings.FACE_RECOGNITION_PROVIDER == 'aws':
        try:
            from .aws_face_service import AWSFaceRecognition
            aws = AWSFaceRecognition()
            face_bytes = base64.b64decode(face_data)
            
            # У AWS немає прямого verify за user, треба authenticate і перевірити user_id
            result = aws.authenticate_face(face_bytes)
            
            if result['success'] and result.get('authenticated'):
                if result.get('user_id') == user.id:
                    return {
                        'success': True,
                        'verified': True,
                        'similarity': result.get('similarity', 0)
                    }
                else:
                    return {
                        'success': True,
                        'verified': False,
                        'error': 'Face belongs to different user'
                    }
            
            return result
        except Exception as e:
            logger.warning(f"AWS verification failed, trying local: {str(e)}")
    
    # Fallback до local
    return FaceRecognitionService.verify_face(user, face_data)


def authenticate_by_face(face_data: str) -> Dict:
    """
    Wrapper function для автентифікації.
    Спробує AWS спочатку, fallback до local.
    """
    if settings.FACE_RECOGNITION_PROVIDER == 'aws':
        try:
            from .aws_face_service import authenticate_face_aws
            result = authenticate_face_aws(face_data)
            
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"AWS authentication failed, trying local: {str(e)}")
    
    # Fallback до local
    return FaceRecognitionService.authenticate_face(face_data)


def delete_user_face_data(user) -> Dict:
    """
    Wrapper function для видалення.
    Видаляє з обох AWS та local.
    """
    results = []
    
    # Видалити з AWS
    if settings.FACE_RECOGNITION_PROVIDER == 'aws':
        try:
            from .aws_face_service import delete_face_aws
            aws_result = delete_face_aws(user)
            results.append(aws_result)
        except Exception as e:
            logger.error(f"AWS deletion failed: {str(e)}")
    
    # Видалити з local
    local_result = FaceRecognitionService.delete_face_data(user)
    results.append(local_result)
    
    # Якщо хоч одне успішне - вважаємо успіхом
    success = any(r.get('success') for r in results)
    
    return {
        'success': success,
        'message': 'Face data deleted',
        'details': results
    }

