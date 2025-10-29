"""
User/Face Recognition Custom Exceptions.
Спеціалізовані exceptions для face recognition.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class FaceRecognitionException(APIException):
    """Базова exception для face recognition"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Face recognition error'
    default_code = 'face_recognition_error'


class FaceNotDetectedException(APIException):
    """Обличчя не знайдено в зображенні"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No face detected in image'
    default_code = 'face_not_detected'


class MultipleFacesException(APIException):
    """Знайдено більше одного обличчя"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Multiple faces detected. Please provide image with single face'
    default_code = 'multiple_faces'


class FaceQualityException(APIException):
    """Якість зображення недостатня"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Face image quality too low'
    default_code = 'low_quality'


class FaceNotRegisteredException(APIException):
    """Обличчя не зареєстровано"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'No face registered for this user'
    default_code = 'face_not_registered'


class FaceAuthenticationFailedException(APIException):
    """Автентифікація не вдалася"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Face authentication failed'
    default_code = 'authentication_failed'


class FaceImageTooLargeException(APIException):
    """Зображення занадто велике"""
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = 'Face image too large'
    default_code = 'image_too_large'


class FaceImageInvalidFormatException(APIException):
    """Невалідний формат зображення"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid image format. Use JPEG or PNG'
    default_code = 'invalid_format'


class BiometricDisabledException(APIException):
    """Біометрія вимкнена для користувача"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Biometric authentication is disabled'
    default_code = 'biometric_disabled'

