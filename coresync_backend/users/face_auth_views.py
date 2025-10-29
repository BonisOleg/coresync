"""
Face Authentication Views.
Окремі endpoints для face recognition автентифікації.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .face_recognition_service import authenticate_by_face
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def face_login(request):
    """
    Автентифікація користувача за обличчям.
    Публічний endpoint для логіну через face recognition.
    
    Request body:
    {
        "face_data": "base64_encoded_image"
    }
    """
    face_data = request.data.get('face_data')
    
    if not face_data:
        return Response({
            'error': 'face_data is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Автентифікувати через face recognition
    result = authenticate_by_face(face_data)
    
    if not result['success']:
        return Response({
            'error': result.get('error', 'Authentication failed')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if not result['authenticated']:
        return Response({
            'error': 'Face not recognized',
            'message': result.get('message', 'No matching face found')
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Отримати користувача
    try:
        user = User.objects.get(id=result['user_id'], is_active=True)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found or inactive'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Генерувати JWT токени
    refresh = RefreshToken.for_user(user)
    
    from .serializers import UserProfileSerializer
    user_data = UserProfileSerializer(user, context={'request': request}).data
    
    return Response({
        'success': True,
        'message': 'Face authentication successful',
        'user': user_data,
        'similarity': result.get('similarity'),
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def face_verify_check(request):
    """
    Перевірити чи face_data відповідає певному користувачу.
    Публічний endpoint для перевірки без автентифікації.
    
    Request body:
    {
        "face_data": "base64_encoded_image"
    }
    
    Returns:
    {
        "verified": true/false,
        "similarity": 0.0-1.0
    }
    """
    face_data = request.data.get('face_data')
    
    if not face_data:
        return Response({
            'error': 'face_data is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = authenticate_by_face(face_data)
    
    if result['success']:
        return Response({
            'verified': result['authenticated'],
            'similarity': result.get('similarity'),
            'message': result.get('message', 'Verification complete')
        })
    else:
        return Response({
            'error': result.get('error', 'Verification failed')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

