"""
Scene Manager Service.
Логіка управління сценами IoT.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..models import Scene, IoTDevice, ControlLog
from .device_controller import DeviceController

logger = logging.getLogger(__name__)


class SceneManager:
    """
    Сервіс для управління сценами.
    Активація, створення та синхронізація сцен.
    """
    
    @staticmethod
    def get_scene(scene_id: int) -> Optional[Scene]:
        """Отримати сцену за ID"""
        try:
            return Scene.objects.get(id=scene_id, is_active=True)
        except Scene.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_scenes(user, include_public: bool = True):
        """Отримати сцени користувача"""
        filters = {'is_active': True}
        
        if include_public:
            # Власні + публічні сцени
            from django.db.models import Q
            return Scene.objects.filter(
                Q(user=user) | Q(is_public=True),
                is_active=True
            ).order_by('-created_at')
        else:
            # Тільки власні
            return Scene.objects.filter(
                user=user,
                is_active=True
            ).order_by('-created_at')
    
    @staticmethod
    def get_public_scenes():
        """Отримати публічні сцени"""
        return Scene.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('-usage_count', 'name')
    
    @classmethod
    def activate_scene(
        cls,
        scene_id: int,
        user=None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """
        Активувати сцену - застосувати всі налаштування пристроїв.
        
        Args:
            scene_id: ID сцени
            user: Користувач що активує
            ip_address: IP адреса клієнта
        
        Returns:
            dict з результатом активації
        """
        scene = cls.get_scene(scene_id)
        
        if not scene:
            return {
                'success': False,
                'error': 'Scene not found',
                'scene_id': scene_id
            }
        
        # Перевірити доступ
        if not scene.is_public and user and scene.user != user:
            return {
                'success': False,
                'error': 'Access denied to this scene',
                'scene_id': scene_id
            }
        
        results = []
        errors = []
        
        try:
            # Застосувати налаштування до кожного пристрою
            for device_id, settings in scene.device_settings.items():
                try:
                    device = IoTDevice.objects.get(
                        device_id=device_id,
                        is_active=True
                    )
                    
                    # Відправити команду на пристрій
                    result = DeviceController.control_device(
                        device_id=device.id,
                        action='set_value',
                        value=settings,
                        user=user,
                        ip_address=ip_address
                    )
                    
                    results.append(result)
                    
                    if not result['success']:
                        errors.append({
                            'device_id': device_id,
                            'error': result.get('error', 'Unknown error')
                        })
                
                except IoTDevice.DoesNotExist:
                    errors.append({
                        'device_id': device_id,
                        'error': 'Device not found'
                    })
                    logger.warning(f"Device {device_id} in scene {scene_id} not found")
            
            # Оновити лічильник використання
            scene.usage_count += 1
            scene.save()
            
            # Залогувати активацію сцени
            cls._log_scene_activation(
                user=user,
                scene=scene,
                success=len(errors) == 0,
                errors=errors,
                ip_address=ip_address
            )
            
            return {
                'success': len(errors) == 0,
                'scene_id': scene_id,
                'scene_name': scene.name,
                'devices_updated': len(results),
                'devices_failed': len(errors),
                'results': results,
                'errors': errors if errors else None,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error activating scene {scene_id}: {str(e)}")
            
            cls._log_scene_activation(
                user=user,
                scene=scene,
                success=False,
                errors=[{'error': str(e)}],
                ip_address=ip_address
            )
            
            return {
                'success': False,
                'error': str(e),
                'scene_id': scene_id
            }
    
    @classmethod
    def create_scene(
        cls,
        name: str,
        description: str,
        device_settings: Dict,
        user,
        scene_type: str = 'custom',
        location: str = '',
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Створити нову сцену.
        
        Args:
            name: Назва сцени
            description: Опис
            device_settings: Налаштування пристроїв (dict)
            user: Користувач-власник
            scene_type: Тип сцени
            location: Локація (опціонально)
            is_public: Публічна сцена
        
        Returns:
            dict з результатом створення
        """
        try:
            # Валідувати device_settings
            if not isinstance(device_settings, dict):
                return {
                    'success': False,
                    'error': 'device_settings must be a dictionary'
                }
            
            # Перевірити існування пристроїв
            device_ids = device_settings.keys()
            existing_devices = IoTDevice.objects.filter(
                device_id__in=device_ids,
                is_active=True
            ).values_list('device_id', flat=True)
            
            invalid_devices = set(device_ids) - set(existing_devices)
            if invalid_devices:
                return {
                    'success': False,
                    'error': f'Invalid device IDs: {", ".join(invalid_devices)}'
                }
            
            # Створити сцену
            scene = Scene.objects.create(
                name=name,
                description=description,
                scene_type=scene_type,
                user=user,
                location=location,
                device_settings=device_settings,
                is_public=is_public
            )
            
            logger.info(f"Scene created: {scene.id} - {name} by {user}")
            
            return {
                'success': True,
                'scene_id': scene.id,
                'scene_name': scene.name,
                'device_count': len(device_settings),
                'created_at': scene.created_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error creating scene: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def update_scene(
        cls,
        scene_id: int,
        user,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Оновити існуючу сцену.
        
        Args:
            scene_id: ID сцени
            user: Користувач
            **kwargs: Поля для оновлення
        
        Returns:
            dict з результатом оновлення
        """
        scene = cls.get_scene(scene_id)
        
        if not scene:
            return {
                'success': False,
                'error': 'Scene not found',
                'scene_id': scene_id
            }
        
        # Перевірити права
        if scene.user != user:
            return {
                'success': False,
                'error': 'You can only edit your own scenes',
                'scene_id': scene_id
            }
        
        try:
            # Оновити поля
            for key, value in kwargs.items():
                if hasattr(scene, key):
                    setattr(scene, key, value)
            
            scene.save()
            
            return {
                'success': True,
                'scene_id': scene_id,
                'scene_name': scene.name,
                'updated_at': scene.updated_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error updating scene {scene_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'scene_id': scene_id
            }
    
    @classmethod
    def delete_scene(cls, scene_id: int, user) -> Dict[str, Any]:
        """
        Видалити сцену (soft delete).
        
        Args:
            scene_id: ID сцени
            user: Користувач
        
        Returns:
            dict з результатом видалення
        """
        scene = cls.get_scene(scene_id)
        
        if not scene:
            return {
                'success': False,
                'error': 'Scene not found',
                'scene_id': scene_id
            }
        
        # Перевірити права
        if scene.user != user and not user.is_staff:
            return {
                'success': False,
                'error': 'You can only delete your own scenes',
                'scene_id': scene_id
            }
        
        try:
            scene.is_active = False
            scene.save()
            
            logger.info(f"Scene deleted: {scene_id} by {user}")
            
            return {
                'success': True,
                'scene_id': scene_id,
                'message': 'Scene deleted successfully'
            }
        
        except Exception as e:
            logger.error(f"Error deleting scene {scene_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'scene_id': scene_id
            }
    
    @staticmethod
    def _log_scene_activation(
        user,
        scene: Scene,
        success: bool,
        errors: list = None,
        ip_address: str = None
    ):
        """Залогувати активацію сцени"""
        try:
            error_message = ''
            if errors:
                error_message = f"Errors: {len(errors)} devices failed. " + \
                               ', '.join([e.get('error', 'Unknown') for e in errors[:3]])
            
            ControlLog.objects.create(
                user=user,
                scene=scene,
                action_type='scene',
                action_description=f"Activated scene: {scene.name}",
                previous_state={},
                new_state=scene.device_settings,
                success=success,
                error_message=error_message,
                ip_address=ip_address
            )
        except Exception as e:
            logger.error(f"Failed to log scene activation: {str(e)}")

