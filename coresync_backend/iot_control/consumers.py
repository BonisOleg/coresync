"""
WebSocket Consumers для IoT Control.
Real-time communication для управління пристроями.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime

logger = logging.getLogger(__name__)


class IoTControlConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для управління IoT пристроями в локації.
    Real-time updates для всіх пристроїв у певній локації.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.location = self.scope['url_route']['kwargs']['location']
        self.user = self.scope.get('user')
        self.room_group_name = f'iot_location_{self.location}'
        
        # Перевірити аутентифікацію
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Приєднатися до group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"IoT WebSocket connected: {self.user.username} to {self.location}")
        
        # Відправити поточний статус пристроїв
        devices_status = await self.get_devices_status(self.location)
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'location': self.location,
            'devices': devices_status,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"IoT WebSocket disconnected: {self.location}, code: {close_code}")
    
    async def receive(self, text_data):
        """
        Отримати команду від клієнта та виконати.
        """
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'control_device':
                await self.handle_device_control(data)
            
            elif command == 'activate_scene':
                await self.handle_scene_activation(data)
            
            elif command == 'get_status':
                await self.handle_status_request(data)
            
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown command: {command}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        
        except Exception as e:
            logger.error(f"Error processing IoT command: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error processing command'
            }))
    
    async def handle_device_control(self, data):
        """Обробити команду управління пристроєм"""
        device_id = data.get('device_id')
        action = data.get('action')
        value = data.get('value')
        
        if not device_id or not action:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'device_id and action are required'
            }))
            return
        
        # Виконати команду
        from .services import DeviceController
        result = await database_sync_to_async(DeviceController.control_device)(
            device_id=device_id,
            action=action,
            value=value,
            user=self.user
        )
        
        # Відправити результат
        await self.send(text_data=json.dumps({
            'type': 'control_result',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Broadcast update до всіх у групі
        if result['success']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'device_update',
                    'device_id': device_id,
                    'status': result.get('new_status'),
                    'user': self.user.username
                }
            )
    
    async def handle_scene_activation(self, data):
        """Обробити активацію сцени"""
        scene_id = data.get('scene_id')
        
        if not scene_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'scene_id is required'
            }))
            return
        
        # Активувати сцену
        from .services import SceneManager
        result = await database_sync_to_async(SceneManager.activate_scene)(
            scene_id=scene_id,
            user=self.user
        )
        
        # Відправити результат
        await self.send(text_data=json.dumps({
            'type': 'scene_activated',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Broadcast update
        if result['success']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'scene_update',
                    'scene_id': scene_id,
                    'scene_name': result.get('scene_name'),
                    'user': self.user.username
                }
            )
    
    async def handle_status_request(self, data):
        """Обробити запит статусу"""
        devices_status = await self.get_devices_status(self.location)
        
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'location': self.location,
            'devices': devices_status,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def device_update(self, event):
        """
        Отримати broadcast update про пристрій.
        Відправити всім підключеним клієнтам.
        """
        await self.send(text_data=json.dumps({
            'type': 'device_update',
            'device_id': event['device_id'],
            'status': event['status'],
            'updated_by': event.get('user'),
            'timestamp': datetime.now().isoformat()
        }))
    
    async def scene_update(self, event):
        """Broadcast update про активацію сцени"""
        await self.send(text_data=json.dumps({
            'type': 'scene_update',
            'scene_id': event['scene_id'],
            'scene_name': event.get('scene_name'),
            'activated_by': event.get('user'),
            'timestamp': datetime.now().isoformat()
        }))
    
    @database_sync_to_async
    def get_devices_status(self, location):
        """Отримати статус всіх пристроїв у локації"""
        from .models import IoTDevice
        from .serializers import IoTDeviceListSerializer
        
        devices = IoTDevice.objects.filter(
            location=location,
            is_active=True
        )
        
        serializer = IoTDeviceListSerializer(devices, many=True)
        return serializer.data


class DeviceStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для моніторингу конкретного пристрою.
    Real-time updates статусу одного пристрою.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.user = self.scope.get('user')
        self.room_group_name = f'iot_device_{self.device_id}'
        
        # Перевірити аутентифікацію
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Приєднатися до group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"Device WebSocket connected: device {self.device_id}")
        
        # Відправити поточний статус
        device_status = await self.get_device_status(self.device_id)
        if device_status:
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'device': device_status,
                'timestamp': datetime.now().isoformat()
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"Device WebSocket disconnected: device {self.device_id}")
    
    async def receive(self, text_data):
        """Отримати команду для пристрою"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'get_status':
                device_status = await self.get_device_status(self.device_id)
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'device': device_status,
                    'timestamp': datetime.now().isoformat()
                }))
        
        except Exception as e:
            logger.error(f"Error in DeviceStatusConsumer: {str(e)}")
    
    @database_sync_to_async
    def get_device_status(self, device_id):
        """Отримати статус пристрою"""
        from .services import DeviceController
        return DeviceController.get_device_status(device_id)


class SensorDataConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для real-time даних сенсорів.
    Стрімінг показань сенсорів пристрою.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.user = self.scope.get('user')
        self.room_group_name = f'iot_sensor_{self.device_id}'
        
        # Перевірити аутентифікацію та права
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Приєднатися до group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"Sensor WebSocket connected: device {self.device_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"Sensor WebSocket disconnected: device {self.device_id}")
    
    async def sensor_reading(self, event):
        """
        Отримати нове показання сенсора.
        Broadcast до всіх підключених клієнтів.
        """
        await self.send(text_data=json.dumps({
            'type': 'sensor_reading',
            'reading_type': event['reading_type'],
            'value': event['value'],
            'unit': event['unit'],
            'quality_score': event.get('quality_score', 1.0),
            'timestamp': event['timestamp']
        }))

