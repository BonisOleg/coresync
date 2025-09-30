"""
Management command to populate sample data for CoreSync.
Safe command that creates test data without conflicts.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import decimal

from services.models import ServiceCategory, Service, ServiceAddon
from memberships.models import MembershipPlan, MembershipBenefit
from users.models import User, UserPreference
from iot_control.models import IoTDevice, Scene


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing data before populating',
        )
    
    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Cleaning existing data...')
            self.clean_data()
        
        self.stdout.write('Creating sample data...')
        
        # Create categories
        mensuite_cat = self.create_service_categories()
        
        # Create membership plans
        self.create_membership_plans()
        
        # Create services
        self.create_services(mensuite_cat)
        
        # Create add-ons
        self.create_service_addons()
        
        # Create IoT devices
        self.create_iot_devices()
        
        # Create sample scenes
        self.create_sample_scenes()
        
        # Create test user
        self.create_test_user()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data!')
        )
    
    def clean_data(self):
        """Clean existing data"""
        ServiceCategory.objects.all().delete()
        Service.objects.all().delete()
        ServiceAddon.objects.all().delete()
        MembershipPlan.objects.all().delete()
        MembershipBenefit.objects.all().delete()
        IoTDevice.objects.all().delete()
        Scene.objects.all().delete()
        # Don't delete users - too risky
    
    def create_service_categories(self):
        """Create service categories"""
        mensuite, _ = ServiceCategory.objects.get_or_create(
            slug='mensuite',
            defaults={
                'name': 'Mensuite',
                'description': 'Advanced men\'s spa services with cutting-edge technology',
                'featured_technologies': ['smart_mirror', 'ai_analyzer', 'meditation_pods'],
                'order': 1
            }
        )
        
        private, _ = ServiceCategory.objects.get_or_create(
            slug='coresync-private',
            defaults={
                'name': 'Coresync Private',
                'description': 'Luxurious couple\'s spa experiences in private suites',
                'featured_technologies': ['immersive_screens', 'ai_massage', 'hot_tub'],
                'order': 2
            }
        )
        
        return mensuite, private
    
    def create_membership_plans(self):
        """Create membership plans"""
        base_plan, _ = MembershipPlan.objects.get_or_create(
            slug='base-tier',
            defaults={
                'name': 'Base Tier',
                'description': 'Essential wellness membership with priority access and significant savings',
                'short_description': '25% discount on all services with priority booking',
                'price': decimal.Decimal('375.00'),
                'duration_months': 12,
                'benefits': [
                    '25% discount on all services',
                    'Priority booking access',
                    'AI Massage Bed with discount',
                    'Backyard access ($150-200/hour)',
                    'Email support'
                ],
                'discount_percentage': 25,
                'mensuite_access': True,
                'coresync_private_access': False,
                'iot_control_access': True,
                'priority_booking': True,
                'monthly_service_credits': 0,
                'guest_passes': 0,
                'featured': False,
                'color_scheme': '#2D4A6B',
                'icon': 'fa-male',
                'order': 1
            }
        )
        
        premium_plan, _ = MembershipPlan.objects.get_or_create(
            slug='premium-tier',
            defaults={
                'name': 'Premium Tier',
                'description': 'Enhanced wellness membership with free services and exclusive perks',
                'short_description': 'Free services included with premium benefits',
                'price': decimal.Decimal('700.00'),
                'duration_months': 12,
                'benefits': [
                    '1-2 free services per month',
                    '1 free AI Massage Bed session',
                    'Discount on Coresync Private',
                    'Discounted Backyard access',
                    'Priority customer support',
                    'Birthday month perks',
                    'Guest pass included'
                ],
                'discount_percentage': 35,
                'mensuite_access': True,
                'coresync_private_access': True,
                'iot_control_access': True,
                'priority_booking': True,
                'monthly_service_credits': 2,
                'guest_passes': 1,
                'featured': True,
                'color_scheme': '#B8860B',
                'icon': 'fa-star',
                'order': 2
            }
        )
        
        unlimited_plan, _ = MembershipPlan.objects.get_or_create(
            slug='unlimited-tier',
            defaults={
                'name': 'Unlimited Tier',
                'description': 'Complete access to all CoreSync services and amenities',
                'short_description': 'Unlimited access to everything CoreSync offers',
                'price': decimal.Decimal('1650.00'),
                'duration_months': 12,
                'benefits': [
                    'Unlimited access to all services',
                    'Unlimited AI Massage Bed sessions',
                    'Unlimited Coresync Private access',
                    'Unlimited Backyard access',
                    'Curated products included',
                    'Concierge service included',
                    'VIP customer support',
                    'Exclusive events access'
                ],
                'discount_percentage': 100,
                'mensuite_access': True,
                'coresync_private_access': True,
                'iot_control_access': True,
                'priority_booking': True,
                'monthly_service_credits': 0,  # 0 means unlimited
                'guest_passes': 5,
                'featured': False,
                'color_scheme': '#1A2635',
                'icon': 'fa-crown',
                'order': 3
            }
        )
        
        return base_plan, premium_plan, unlimited_plan
    
    def create_services(self, categories):
        """Create sample services"""
        mensuite_cat, private_cat = categories
        
        # Mensuite Services
        services_data = [
            {
                'name': 'AI Massage Therapy',
                'slug': 'ai-massage-therapy',
                'description': 'Advanced AI-guided massage with personalized pressure and technique optimization.',
                'short_description': 'Personalized AI massage experience',
                'category': mensuite_cat,
                'member_price': decimal.Decimal('150.00'),
                'non_member_price': decimal.Decimal('200.00'),
                'duration': 60,
                'featured': True
            },
            {
                'name': 'Precision Facial',
                'slug': 'precision-facial',
                'description': 'Advanced facial treatment with smart mirror analysis and customized skincare.',
                'short_description': 'AI-analyzed facial treatment',
                'category': mensuite_cat,
                'member_price': decimal.Decimal('120.00'),
                'non_member_price': decimal.Decimal('180.00'),
                'duration': 45,
                'featured': True
            },
            {
                'name': 'Executive Barber Service',
                'slug': 'executive-barber',
                'description': 'Premium barbering service with traditional techniques and modern precision.',
                'short_description': 'Professional grooming service',
                'category': mensuite_cat,
                'member_price': decimal.Decimal('90.00'),
                'non_member_price': decimal.Decimal('120.00'),
                'duration': 45,
                'featured': False
            },
            {
                'name': 'Deep Tissue Massage',
                'slug': 'deep-tissue-massage',
                'description': 'Therapeutic deep tissue massage for muscle recovery and stress relief.',
                'short_description': 'Therapeutic muscle recovery',
                'category': mensuite_cat,
                'member_price': decimal.Decimal('180.00'),
                'non_member_price': decimal.Decimal('240.00'),
                'duration': 75,
                'featured': False
            },
            {
                'name': 'Laser Hair Removal',
                'slug': 'laser-hair-removal',
                'description': 'Professional laser hair removal with latest technology.',
                'short_description': 'Advanced laser treatment',
                'category': mensuite_cat,
                'member_price': decimal.Decimal('100.00'),
                'non_member_price': decimal.Decimal('150.00'),
                'duration': 30,
                'featured': False
            },
            # Coresync Private Services
            {
                'name': 'Ultimate Couple Experience',
                'slug': 'ultimate-couple',
                'description': 'Complete couple\'s spa experience with private suite access.',
                'short_description': 'Luxury couple\'s wellness journey',
                'category': private_cat,
                'member_price': decimal.Decimal('300.00'),
                'non_member_price': decimal.Decimal('400.00'),
                'duration': 120,
                'max_capacity': 2,
                'featured': True
            },
            {
                'name': 'Romantic Hot Tub Session',
                'slug': 'romantic-hot-tub',
                'description': 'Private hot tub experience with champagne and aromatherapy.',
                'short_description': 'Private hot tub experience',
                'category': private_cat,
                'member_price': decimal.Decimal('150.00'),
                'non_member_price': decimal.Decimal('200.00'),
                'duration': 60,
                'max_capacity': 2,
                'featured': True
            },
            {
                'name': 'Couple\'s Massage',
                'slug': 'couples-massage',
                'description': 'Side-by-side massage experience in our private suite.',
                'short_description': 'Synchronized couple\'s massage',
                'category': private_cat,
                'member_price': decimal.Decimal('400.00'),
                'non_member_price': decimal.Decimal('500.00'),
                'duration': 90,
                'max_capacity': 2,
                'featured': False
            }
        ]
        
        for service_data in services_data:
            Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data
            )
    
    def create_service_addons(self):
        """Create service add-ons"""
        addons_data = [
            {
                'name': 'LED Light Therapy',
                'description': 'Advanced LED light treatment for skin rejuvenation',
                'price': decimal.Decimal('50.00'),
                'available_for_all_services': True
            },
            {
                'name': 'Aromatherapy Enhancement',
                'description': 'Premium essential oils and scents',
                'price': decimal.Decimal('25.00'),
                'available_for_all_services': True
            },
            {
                'name': 'Hot Stone Add-on',
                'description': 'Heated volcanic stones for deeper relaxation',
                'price': decimal.Decimal('40.00'),
                'available_for_all_services': False
            },
            {
                'name': 'Oxygen Treatment',
                'description': 'Pure oxygen therapy for enhanced wellness',
                'price': decimal.Decimal('60.00'),
                'available_for_all_services': True
            }
        ]
        
        for addon_data in addons_data:
            ServiceAddon.objects.get_or_create(
                name=addon_data['name'],
                defaults=addon_data
            )
    
    def create_iot_devices(self):
        """Create IoT device samples"""
        devices_data = [
            {
                'name': 'Main Lighting System',
                'device_type': 'lighting',
                'location': 'mensuite_main',
                'device_id': 'light_mens_001',
                'current_status': {'brightness': 70, 'color': '#ff9500', 'mode': 'warm'},
                'is_online': True,
                'min_value': 0,
                'max_value': 100,
                'default_value': 50
            },
            {
                'name': 'Scent Diffuser Pro',
                'device_type': 'scent',
                'location': 'coresync_suite',
                'device_id': 'scent_cs_001',
                'current_status': {'intensity': 3, 'scent': 'lavender', 'active': True},
                'is_online': True,
                'min_value': 1,
                'max_value': 5,
                'default_value': 3
            },
            {
                'name': 'Climate Control',
                'device_type': 'temperature',
                'location': 'mensuite_main',
                'device_id': 'temp_mens_001',
                'current_status': {'temperature': 72.5, 'humidity': 45, 'mode': 'auto'},
                'is_online': True,
                'min_value': 65,
                'max_value': 80,
                'default_value': 72
            }
        ]
        
        for device_data in devices_data:
            IoTDevice.objects.get_or_create(
                device_id=device_data['device_id'],
                defaults=device_data
            )
    
    def create_sample_scenes(self):
        """Create sample IoT scenes"""
        scenes_data = [
            {
                'name': 'Swiss Alps',
                'description': 'Mountain relaxation scene with alpine atmosphere',
                'scene_type': 'preset',
                'location': 'coresync_suite',
                'device_settings': {
                    'lighting': {'brightness': 60, 'color': '#87CEEB'},
                    'scent': {'type': 'alpine', 'intensity': 3},
                    'temperature': 70,
                    'music': {'playlist': 'nature_sounds', 'volume': 25}
                },
                'is_public': True,
                'usage_count': 245
            },
            {
                'name': 'Venice Canals',
                'description': 'Romantic Venice atmosphere with water sounds',
                'scene_type': 'preset',
                'location': 'coresync_suite',
                'device_settings': {
                    'lighting': {'brightness': 45, 'color': '#FFD700'},
                    'scent': {'type': 'italian_cypress', 'intensity': 2},
                    'temperature': 74,
                    'music': {'playlist': 'venice_ambience', 'volume': 20}
                },
                'is_public': True,
                'usage_count': 189
            },
            {
                'name': 'Executive Focus',
                'description': 'Energizing environment for business professionals',
                'scene_type': 'preset',
                'location': 'mensuite_main',
                'device_settings': {
                    'lighting': {'brightness': 85, 'color': '#FFFFFF'},
                    'scent': {'type': 'eucalyptus', 'intensity': 4},
                    'temperature': 68,
                    'music': {'playlist': 'focus_ambient', 'volume': 15}
                },
                'is_public': True,
                'usage_count': 167
            }
        ]
        
        for scene_data in scenes_data:
            Scene.objects.get_or_create(
                name=scene_data['name'],
                scene_type=scene_data['scene_type'],
                defaults=scene_data
            )
    
    def create_test_user(self):
        """Create test user with preferences"""
        try:
            user, created = User.objects.get_or_create(
                email='test@coresync.life',
                defaults={
                    'username': 'testuser',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone': '+1-555-0123',
                    'membership_status': 'premium',
                    'is_staff': False,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                
                # Create user preferences
                UserPreference.objects.create(
                    user=user,
                    default_scene_name='Swiss Alps',
                    scene_config={
                        'lighting': {'brightness': 60, 'color': '#87CEEB'},
                        'temperature': 70
                    },
                    favorite_scents=['lavender', 'eucalyptus'],
                    scent_intensity=3,
                    lighting_type='warm',
                    lighting_intensity=70,
                    preferred_temperature=72.0,
                    music_genre='ambient',
                    music_volume=30
                )
                
                self.stdout.write(f'Created test user: {user.email} / testpass123')
            else:
                self.stdout.write(f'Test user already exists: {user.email}')
                
        except Exception as e:
            self.stdout.write(f'Error creating test user: {e}')




