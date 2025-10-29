"""
IoT Control Views для CoreSync API.
REST API endpoints для управління IoT пристроями та сценами.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import IoTDevice, Scene, ControlLog, SensorReading
from .serializers import (
    IoTDeviceSerializer,
    IoTDeviceListSerializer,
    DeviceControlSerializer,
    SceneSerializer,
    SceneListSerializer,
    SceneActivationSerializer,
    ControlLogSerializer,
    SensorReadingSerializer,
    LightingControlSerializer,
    TemperatureControlSerializer,
    ScentControlSerializer,
    MusicControlSerializer
)
from .permissions import IsMemberUser, IsDeviceOwnerOrPublic, IsAdminOrReadOnly
from .services import DeviceController, SceneManager
from .utils import get_client_ip


class IoTDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet для управління IoT пристроями"""
    
    queryset = IoTDevice.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsMemberUser]
    
    def get_serializer_class(self):
        """Вибрати serializer в залежності від action"""
        if self.action == 'list':
            return IoTDeviceListSerializer
        return IoTDeviceSerializer
    
    def get_queryset(self):
        """Фільтрувати пристрої за локацією"""
        queryset = super().get_queryset()
        
        location = self.request.query_params.get('location', None)
        device_type = self.request.query_params.get('type', None)
        
        if location:
            queryset = queryset.filter(location=location)
        
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        return queryset.order_by('location', 'device_type', 'name')
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Отримати пристрої за локацією"""
        location = request.query_params.get('location')
        
        if not location:
            return Response(
                {'error': 'location parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        devices = DeviceController.get_devices_by_location(location)
        serializer = IoTDeviceListSerializer(devices, many=True)
        
        return Response({
            'location': location,
            'count': len(devices),
            'devices': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Отримати статус конкретного пристрою"""
        device_status = DeviceController.get_device_status(pk)
        
        if not device_status:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(device_status)
    
    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        """Управління конкретним пристроєм"""
        serializer = DeviceControlSerializer(data={
            'device_id': pk,
            **request.data
        })
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = DeviceController.control_device(
            device_id=pk,
            action=serializer.validated_data['action'],
            value=serializer.validated_data.get('value'),
            user=request.user,
            ip_address=get_client_ip(request)
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def lighting(self, request):
        """Управління освітленням"""
        serializer = LightingControlSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = DeviceController.control_lighting(
            location=serializer.validated_data['location'],
            brightness=serializer.validated_data['brightness'],
            color=serializer.validated_data.get('color'),
            user=request.user,
            ip_address=get_client_ip(request)
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def temperature(self, request):
        """Управління температурою"""
        serializer = TemperatureControlSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = DeviceController.control_temperature(
            location=serializer.validated_data['location'],
            temperature=serializer.validated_data['temperature'],
            user=request.user,
            ip_address=get_client_ip(request)
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    


class SceneViewSet(viewsets.ModelViewSet):
    """ViewSet для управління сценами"""
    
    queryset = Scene.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsMemberUser, IsDeviceOwnerOrPublic]
    
    def get_serializer_class(self):
        """Вибрати serializer"""
        if self.action == 'list':
            return SceneListSerializer
        return SceneSerializer
    
    def get_queryset(self):
        """Отримати сцени користувача + публічні"""
        user = self.request.user
        
        # Фільтри з query params
        scene_type = self.request.query_params.get('type', None)
        location = self.request.query_params.get('location', None)
        public_only = self.request.query_params.get('public', None)
        
        if public_only == 'true':
            queryset = Scene.objects.filter(is_public=True, is_active=True)
        else:
            from django.db.models import Q
            queryset = Scene.objects.filter(
                Q(user=user) | Q(is_public=True),
                is_active=True
            )
        
        if scene_type:
            queryset = queryset.filter(scene_type=scene_type)
        
        if location:
            queryset = queryset.filter(location=location)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Створити нову сцену"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_scenes(self, request):
        """Отримати тільки власні сцени"""
        scenes = SceneManager.get_user_scenes(request.user, include_public=False)
        serializer = SceneListSerializer(scenes, many=True)
        
        return Response({
            'count': len(scenes),
            'scenes': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def public_scenes(self, request):
        """Отримати публічні сцени"""
        scenes = SceneManager.get_public_scenes()
        serializer = SceneListSerializer(scenes, many=True)
        
        return Response({
            'count': len(scenes),
            'scenes': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активувати сцену"""
        result = SceneManager.activate_scene(
            scene_id=pk,
            user=request.user,
            ip_address=get_client_ip(request)
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Дублювати сцену"""
        original_scene = SceneManager.get_scene(pk)
        
        if not original_scene:
            return Response(
                {'error': 'Scene not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Створити копію
        new_name = request.data.get('name', f"{original_scene.name} (Copy)")
        
        result = SceneManager.create_scene(
            name=new_name,
            description=original_scene.description,
            device_settings=original_scene.device_settings.copy(),
            user=request.user,
            scene_type='custom',
            location=original_scene.location,
            is_public=False
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class ControlLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для перегляду логів управління (read-only)"""
    
    queryset = ControlLog.objects.all()
    serializer_class = ControlLogSerializer
    permission_classes = [IsAuthenticated, IsMemberUser]
    
    def get_queryset(self):
        """Фільтрувати логи"""
        queryset = super().get_queryset()
        
        # Користувачі бачать тільки свої логи
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Фільтри
        device_id = self.request.query_params.get('device', None)
        action_type = self.request.query_params.get('action_type', None)
        success = self.request.query_params.get('success', None)
        
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        return queryset.order_by('-timestamp')[:100]  # Останні 100 записів
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Отримати останні дії користувача"""
        limit = int(request.query_params.get('limit', 20))
        
        logs = ControlLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:limit]
        
        serializer = self.get_serializer(logs, many=True)
        
        return Response({
            'count': len(logs),
            'logs': serializer.data
        })


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для показань сенсорів (read-only)"""
    
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Фільтрувати показання сенсорів"""
        queryset = super().get_queryset()
        
        device_id = self.request.query_params.get('device', None)
        reading_type = self.request.query_params.get('type', None)
        
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        if reading_type:
            queryset = queryset.filter(reading_type=reading_type)
        
        return queryset.order_by('-timestamp')[:100]

