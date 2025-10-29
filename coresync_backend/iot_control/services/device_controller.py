"""
Device Controller Service.
Логіка управління IoT пристроями.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..models import IoTDevice, ControlLog

logger = logging.getLogger(__name__)


class DeviceController:
    """
    Сервіс для управління IoT пристроями.
    Обробляє команди та логує всі дії.
    """
    
    @staticmethod
    def get_device(device_id: int) -> Optional[IoTDevice]:
        """Отримати пристрій за ID"""
        try:
            return IoTDevice.objects.get(id=device_id, is_active=True)
        except IoTDevice.DoesNotExist:
            return None
    
    @staticmethod
    def get_devices_by_location(location: str) -> list:
        """Отримати всі пристрої в локації"""
        return IoTDevice.objects.filter(
            location=location,
            is_active=True
        ).order_by('device_type', 'name')
    
    @staticmethod
    def get_devices_by_type(device_type: str, location: str = None) -> list:
        """Отримати пристрої за типом"""
        filters = {'device_type': device_type, 'is_active': True}
        if location:
            filters['location'] = location
        
        return IoTDevice.objects.filter(**filters)
    
    @classmethod
    def control_device(
        cls,
        device_id: int,
        action: str,
        value: Any = None,
        user=None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """
        Відправити команду на пристрій.
        
        Args:
            device_id: ID пристрою
            action: Дія (set_value, turn_on, turn_off, adjust)
            value: Значення (опціонально)
            user: Користувач що виконує дію
            ip_address: IP адреса клієнта
        
        Returns:
            dict з результатом операції
        """
        device = cls.get_device(device_id)
        
        if not device:
            return {
                'success': False,
                'error': 'Device not found',
                'device_id': device_id
            }
        
        # Зберегти попередній стан
        previous_state = device.current_status.copy()
        
        try:
            # Виконати дію на основі типу
            new_status = cls._execute_action(device, action, value)
            
            # Оновити статус пристрою
            device.current_status = new_status
            device.is_online = True
            device.save()
            
            # Залогувати дію
            cls._log_control_action(
                user=user,
                device=device,
                action_type='manual',
                action_description=f"{action} on {device.name}",
                previous_state=previous_state,
                new_state=new_status,
                success=True,
                ip_address=ip_address
            )
            
            return {
                'success': True,
                'device_id': device_id,
                'device_name': device.name,
                'action': action,
                'new_status': new_status,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error controlling device {device_id}: {str(e)}")
            
            # Залогувати помилку
            cls._log_control_action(
                user=user,
                device=device,
                action_type='manual',
                action_description=f"Failed: {action} on {device.name}",
                previous_state=previous_state,
                new_state={},
                success=False,
                error_message=str(e),
                ip_address=ip_address
            )
            
            return {
                'success': False,
                'error': str(e),
                'device_id': device_id
            }
    
    @staticmethod
    def _execute_action(device: IoTDevice, action: str, value: Any) -> Dict:
        """
        Виконати конкретну дію на пристрої.
        PLACEHOLDER - тут буде реальна інтеграція з обладнанням.
        """
        current_status = device.current_status.copy()
        
        if action == 'turn_on':
            current_status['power'] = 'on'
            current_status['last_action'] = 'turn_on'
        
        elif action == 'turn_off':
            current_status['power'] = 'off'
            current_status['last_action'] = 'turn_off'
        
        elif action == 'set_value':
            if isinstance(value, dict):
                current_status.update(value)
            else:
                current_status['value'] = value
            current_status['last_action'] = 'set_value'
        
        elif action == 'adjust':
            if isinstance(value, dict):
                # Merge з існуючим status
                for key, val in value.items():
                    current_status[key] = val
            current_status['last_action'] = 'adjust'
        
        # Додати timestamp
        current_status['last_update'] = datetime.now().isoformat()
        
        return current_status
    
    @classmethod
    def control_lighting(
        cls,
        location: str,
        brightness: int,
        color: str = None,
        user=None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """Управління освітленням в локації"""
        devices = cls.get_devices_by_type('lighting', location)
        
        if not devices:
            return {
                'success': False,
                'error': f'No lighting devices found in {location}'
            }
        
        results = []
        for device in devices:
            value = {'brightness': brightness}
            if color:
                value['color'] = color
            
            result = cls.control_device(
                device_id=device.id,
                action='set_value',
                value=value,
                user=user,
                ip_address=ip_address
            )
            results.append(result)
        
        return {
            'success': True,
            'location': location,
            'brightness': brightness,
            'color': color,
            'devices_updated': len(results),
            'results': results
        }
    
    @classmethod
    def control_temperature(
        cls,
        location: str,
        temperature: float,
        user=None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """Управління температурою в локації"""
        devices = cls.get_devices_by_type('temperature', location)
        
        if not devices:
            return {
                'success': False,
                'error': f'No temperature control devices found in {location}'
            }
        
        results = []
        for device in devices:
            result = cls.control_device(
                device_id=device.id,
                action='set_value',
                value={'temperature': temperature, 'unit': 'fahrenheit'},
                user=user,
                ip_address=ip_address
            )
            results.append(result)
        
        return {
            'success': True,
            'location': location,
            'temperature': temperature,
            'devices_updated': len(results),
            'results': results
        }
    
    @staticmethod
    def _log_control_action(
        user,
        device: IoTDevice,
        action_type: str,
        action_description: str,
        previous_state: Dict,
        new_state: Dict,
        success: bool,
        error_message: str = '',
        ip_address: str = None
    ):
        """Створити лог запис про дію управління"""
        try:
            ControlLog.objects.create(
                user=user,
                device=device,
                action_type=action_type,
                action_description=action_description,
                previous_state=previous_state,
                new_state=new_state,
                success=success,
                error_message=error_message,
                ip_address=ip_address
            )
        except Exception as e:
            logger.error(f"Failed to log control action: {str(e)}")
    
    @classmethod
    def get_device_status(cls, device_id: int) -> Optional[Dict]:
        """Отримати поточний статус пристрою"""
        device = cls.get_device(device_id)
        
        if not device:
            return None
        
        return {
            'device_id': device.id,
            'device_name': device.name,
            'device_type': device.device_type,
            'location': device.location,
            'is_online': device.is_online,
            'current_status': device.current_status,
            'last_updated': device.last_updated.isoformat() if device.last_updated else None
        }

