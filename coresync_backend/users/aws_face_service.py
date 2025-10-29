"""
AWS Rekognition Face Recognition Service.
Production-ready інтеграція з AWS Rekognition для face recognition.
"""
import boto3
import base64
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AWSFaceRecognitionError(Exception):
    """Custom exception для AWS face recognition помилок"""
    pass


class AWSFaceRecognition:
    """
    AWS Rekognition service wrapper.
    Забезпечує face registration, authentication та management.
    """
    
    def __init__(self):
        """Ініціалізувати AWS Rekognition client"""
        try:
            self.client = boto3.client(
                'rekognition',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.collection_id = settings.AWS_REKOGNITION_COLLECTION_ID
            self._ensure_collection_exists()
        except Exception as e:
            logger.error(f"Failed to initialize AWS Rekognition: {str(e)}")
            raise AWSFaceRecognitionError("AWS Rekognition initialization failed")
    
    def _ensure_collection_exists(self):
        """
        Перевірити існування collection, створити якщо відсутнє.
        Collection = база даних face templates в AWS.
        """
        cache_key = f'aws_collection_exists:{self.collection_id}'
        
        # Перевірити cache
        if cache.get(cache_key):
            return
        
        try:
            self.client.describe_collection(CollectionId=self.collection_id)
            cache.set(cache_key, True, 3600)  # Cache на 1 годину
            logger.info(f"AWS Collection '{self.collection_id}' exists")
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Collection не існує - створити
                try:
                    self.client.create_collection(CollectionId=self.collection_id)
                    cache.set(cache_key, True, 3600)
                    logger.info(f"Created AWS Collection: {self.collection_id}")
                except Exception as create_error:
                    logger.error(f"Failed to create collection: {str(create_error)}")
                    raise AWSFaceRecognitionError("Failed to create face collection")
            else:
                logger.error(f"AWS Collection check failed: {str(e)}")
                raise AWSFaceRecognitionError("Collection verification failed")
    
    def register_face(
        self,
        user_id: int,
        face_image: bytes,
        max_faces: int = 1
    ) -> Dict[str, Any]:
        """
        Зареєструвати обличчя користувача в AWS Rekognition.
        
        Args:
            user_id: ID користувача (використовується як ExternalImageId)
            face_image: bytes зображення в JPEG або PNG
            max_faces: максимум облич для індексації (default 1)
        
        Returns:
            dict з результатом реєстрації
        """
        try:
            # Валідувати розмір зображення
            max_size = settings.FACE_MAX_IMAGE_SIZE_MB * 1024 * 1024
            if len(face_image) > max_size:
                return {
                    'success': False,
                    'error': f'Image too large (max {settings.FACE_MAX_IMAGE_SIZE_MB}MB)'
                }
            
            # Index faces в AWS Rekognition
            response = self.client.index_faces(
                CollectionId=self.collection_id,
                Image={'Bytes': face_image},
                ExternalImageId=str(user_id),
                MaxFaces=max_faces,
                QualityFilter='AUTO',  # Автоматично відкидає погані фото
                DetectionAttributes=['ALL']
            )
            
            # Перевірити чи знайдено обличчя
            if not response.get('FaceRecords'):
                return {
                    'success': False,
                    'error': 'No face detected in image'
                }
            
            face_record = response['FaceRecords'][0]
            face_detail = face_record.get('FaceDetail', {})
            
            # Перевірити якість
            quality = face_detail.get('Quality', {})
            brightness = quality.get('Brightness', 0)
            sharpness = quality.get('Sharpness', 0)
            
            quality_score = (brightness + sharpness) / 2
            
            if quality_score < settings.FACE_QUALITY_THRESHOLD:
                # Видалити погане обличчя
                self.client.delete_faces(
                    CollectionId=self.collection_id,
                    FaceIds=[face_record['Face']['FaceId']]
                )
                return {
                    'success': False,
                    'error': 'Image quality too low',
                    'quality_score': round(quality_score, 2)
                }
            
            logger.info(f"Face registered for user {user_id}")
            
            return {
                'success': True,
                'face_id': face_record['Face']['FaceId'],
                'image_id': face_record['Face']['ImageId'],
                'confidence': face_record['Face']['Confidence'],
                'quality': {
                    'brightness': brightness,
                    'sharpness': sharpness,
                    'score': round(quality_score, 2)
                },
                'bounding_box': face_record['Face'].get('BoundingBox', {}),
                'landmarks': len(face_detail.get('Landmarks', []))
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"AWS Rekognition error [{error_code}]: {error_message}")
            
            return {
                'success': False,
                'error': f'AWS Error: {error_message}',
                'error_code': error_code
            }
        
        except Exception as e:
            logger.exception(f"Unexpected error registering face: {str(e)}")
            return {
                'success': False,
                'error': 'Internal error during face registration'
            }
    
    def authenticate_face(
        self,
        face_image: bytes,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Знайти користувача за обличчям.
        
        Args:
            face_image: bytes зображення
            threshold: мінімальна схожість (0-100). Default з settings
        
        Returns:
            dict з результатом автентифікації та user_id якщо знайдено
        """
        if threshold is None:
            threshold = settings.FACE_SIMILARITY_THRESHOLD
        
        try:
            # Пошук faces в collection
            response = self.client.search_faces_by_image(
                CollectionId=self.collection_id,
                Image={'Bytes': face_image},
                FaceMatchThreshold=threshold,
                MaxFaces=1,
                QualityFilter='AUTO'
            )
            
            # Перевірити чи знайдено співпадіння
            if not response.get('FaceMatches'):
                return {
                    'success': True,
                    'authenticated': False,
                    'message': 'No matching face found',
                    'searched_faces': response.get('SearchedFaceConfidence', 0)
                }
            
            # Найкраще співпадіння
            match = response['FaceMatches'][0]
            matched_face = match['Face']
            similarity = match['Similarity']
            
            # Витягти user_id з ExternalImageId
            try:
                user_id = int(matched_face['ExternalImageId'])
            except (ValueError, KeyError):
                logger.error(f"Invalid ExternalImageId: {matched_face.get('ExternalImageId')}")
                return {
                    'success': False,
                    'error': 'Invalid face record in database'
                }
            
            logger.info(
                f"Face authenticated: user_id={user_id}, "
                f"similarity={similarity:.2f}%"
            )
            
            return {
                'success': True,
                'authenticated': True,
                'user_id': user_id,
                'similarity': round(similarity, 2),
                'confidence': matched_face.get('Confidence', 0),
                'face_id': matched_face.get('FaceId')
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"AWS search error [{error_code}]: {error_message}")
            
            # Специфічні помилки
            if error_code == 'InvalidImageFormatException':
                return {
                    'success': False,
                    'error': 'Invalid image format. Use JPEG or PNG'
                }
            elif error_code == 'ImageTooLargeException':
                return {
                    'success': False,
                    'error': f'Image too large (max {settings.FACE_MAX_IMAGE_SIZE_MB}MB)'
                }
            else:
                return {
                    'success': False,
                    'error': f'Authentication failed: {error_message}'
                }
        
        except Exception as e:
            logger.exception(f"Unexpected error in face authentication: {str(e)}")
            return {
                'success': False,
                'error': 'Internal error during authentication'
            }
    
    def delete_face(self, user_id: int) -> Dict[str, Any]:
        """
        Видалити обличчя користувача з AWS Rekognition.
        
        Args:
            user_id: ID користувача
        
        Returns:
            dict з результатом видалення
        """
        try:
            # Знайти face_ids користувача
            response = self.client.list_faces(
                CollectionId=self.collection_id,
                MaxResults=100
            )
            
            # Фільтрувати faces за ExternalImageId
            face_ids = [
                face['FaceId']
                for face in response.get('Faces', [])
                if face.get('ExternalImageId') == str(user_id)
            ]
            
            if not face_ids:
                logger.warning(f"No faces found for user {user_id}")
                return {
                    'success': True,
                    'message': 'No faces to delete',
                    'deleted_count': 0
                }
            
            # Видалити faces
            delete_response = self.client.delete_faces(
                CollectionId=self.collection_id,
                FaceIds=face_ids
            )
            
            deleted_count = len(delete_response.get('DeletedFaces', []))
            
            logger.info(f"Deleted {deleted_count} faces for user {user_id}")
            
            return {
                'success': True,
                'message': f'Successfully deleted {deleted_count} face(s)',
                'deleted_count': deleted_count
            }
        
        except ClientError as e:
            logger.error(f"AWS delete error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        
        except Exception as e:
            logger.exception(f"Unexpected error deleting face: {str(e)}")
            return {
                'success': False,
                'error': 'Internal error during deletion'
            }
    
    def verify_face(
        self,
        face_id: str,
        target_face_image: bytes,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Порівняти два обличчя (verify mode).
        Використовується для додаткової перевірки.
        
        Args:
            face_id: ID обличчя в collection
            target_face_image: bytes нового зображення для порівняння
            threshold: поріг схожості
        
        Returns:
            dict з результатом порівняння
        """
        if threshold is None:
            threshold = settings.FACE_SIMILARITY_THRESHOLD
        
        try:
            response = self.client.compare_faces(
                SourceImage={'S3Object': {'Bucket': '', 'Name': ''}},  # Не використовується
                TargetImage={'Bytes': target_face_image},
                SimilarityThreshold=threshold
            )
            
            if not response.get('FaceMatches'):
                return {
                    'success': True,
                    'verified': False,
                    'similarity': 0
                }
            
            match = response['FaceMatches'][0]
            similarity = match['Similarity']
            
            return {
                'success': True,
                'verified': similarity >= threshold,
                'similarity': round(similarity, 2),
                'confidence': match['Face'].get('Confidence', 0)
            }
        
        except Exception as e:
            logger.error(f"Face verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_faces(self, face_image: bytes) -> Dict[str, Any]:
        """
        Detect faces в зображенні без збереження.
        Використовується для валідації перед реєстрацією.
        """
        try:
            response = self.client.detect_faces(
                Image={'Bytes': face_image},
                Attributes=['ALL']
            )
            
            face_details = response.get('FaceDetails', [])
            
            if not face_details:
                return {
                    'success': True,
                    'faces_count': 0,
                    'message': 'No faces detected'
                }
            
            # Аналіз першого обличчя
            face = face_details[0]
            quality = face.get('Quality', {})
            
            return {
                'success': True,
                'faces_count': len(face_details),
                'confidence': face.get('Confidence', 0),
                'quality': {
                    'brightness': quality.get('Brightness', 0),
                    'sharpness': quality.get('Sharpness', 0)
                },
                'emotions': face.get('Emotions', []),
                'age_range': face.get('AgeRange', {}),
                'gender': face.get('Gender', {}),
                'eyes_open': face.get('EyesOpen', {}).get('Value', False),
                'mouth_open': face.get('MouthOpen', {}).get('Value', False),
                'smile': face.get('Smile', {}).get('Value', False)
            }
        
        except Exception as e:
            logger.error(f"Face detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def register_face_aws(user, face_data: str) -> Dict[str, Any]:
    """
    Wrapper function для реєстрації face через AWS.
    
    Args:
        user: User instance
        face_data: base64 encoded image
    
    Returns:
        dict з результатом
    """
    try:
        # Decode base64
        face_bytes = base64.b64decode(face_data)
        
        # Створити AWS service
        aws_service = AWSFaceRecognition()
        
        # Зареєструвати обличчя
        result = aws_service.register_face(user.id, face_bytes)
        
        # Зберегти в БД якщо успішно
        if result['success']:
            user.face_recognition_data = result['face_id']
            user.biometric_enabled = True
            user.save()
            
            logger.info(f"Face registered successfully for user {user.id}")
        
        return result
    
    except Exception as e:
        logger.exception(f"Error in register_face_aws: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to register face'
        }


def authenticate_face_aws(face_data: str) -> Dict[str, Any]:
    """
    Wrapper function для автентифікації через AWS.
    
    Args:
        face_data: base64 encoded image
    
    Returns:
        dict з результатом та user_id якщо знайдено
    """
    try:
        # Decode base64
        face_bytes = base64.b64decode(face_data)
        
        # Створити AWS service
        aws_service = AWSFaceRecognition()
        
        # Автентифікувати
        result = aws_service.authenticate_face(face_bytes)
        
        return result
    
    except Exception as e:
        logger.exception(f"Error in authenticate_face_aws: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to authenticate face'
        }


def delete_face_aws(user) -> Dict[str, Any]:
    """
    Wrapper function для видалення face з AWS.
    
    Args:
        user: User instance
    
    Returns:
        dict з результатом
    """
    try:
        aws_service = AWSFaceRecognition()
        result = aws_service.delete_face(user.id)
        
        if result['success']:
            user.face_recognition_data = None
            user.biometric_enabled = False
            user.save()
        
        return result
    
    except Exception as e:
        logger.exception(f"Error in delete_face_aws: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to delete face'
        }

