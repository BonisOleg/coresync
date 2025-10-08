"""
Comprehensive test suite for CoreSync backend.
Tests all apps and major functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from shop.models import Product, PickupOrder, OrderItem
from concierge.models import ConciergeRequest
from services.models import Service, ServiceCategory
from memberships.models import MembershipPlan, Membership

User = get_user_model()


class ShopAPITestCase(APITestCase):
    """Test Shop app functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testshop',
            email='testshop@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Shop'
        )
        self.client.force_login(self.user)
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Test Serum',
            slug='test-serum',
            category='skincare',
            description='Test description',
            short_description='Test',
            price=100.00,
            member_price=80.00,
            stock=10,
        )
        
        self.product2 = Product.objects.create(
            name='Test Cream',
            slug='test-cream',
            category='skincare',
            description='Test description',
            short_description='Test',
            price=150.00,
            member_price=120.00,
            stock=5,
        )
    
    def test_list_products(self):
        """Test product listing."""
        response = self.client.get('/api/shop/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)
    
    def test_product_detail(self):
        """Test product detail by slug."""
        response = self.client.get(f'/api/shop/products/{self.product1.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], 'Test Serum')
    
    def test_create_order(self):
        """Test order creation."""
        order_data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': 2,
                }
            ]
        }
        response = self.client.post(
            '/api/shop/orders/create_order/',
            data=order_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('order_number', data)
        self.assertTrue(data['order_number'].startswith('PO-'))
    
    def test_stock_decreases_after_order(self):
        """Test stock management."""
        initial_stock = self.product1.stock
        
        order_data = {
            'items': [{'product_id': self.product1.id, 'quantity': 2}]
        }
        self.client.post(
            '/api/shop/orders/create_order/',
            data=order_data,
            content_type='application/json'
        )
        
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, initial_stock - 2)
    
    def test_insufficient_stock(self):
        """Test insufficient stock error."""
        order_data = {
            'items': [{'product_id': self.product1.id, 'quantity': 100}]
        }
        response = self.client.post(
            '/api/shop/orders/create_order/',
            data=order_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_order(self):
        """Test order cancellation."""
        # Create order
        order = PickupOrder.objects.create(user=self.user)
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=self.product1.member_price
        )
        
        initial_stock = self.product1.stock
        
        # Cancel order
        response = self.client.post(f'/api/shop/orders/{order.id}/cancel_order/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check stock restored
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, initial_stock + 2)


class ConciergeAPITestCase(APITestCase):
    """Test Concierge app functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testconcierge',
            email='testconcierge@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Concierge'
        )
        self.client.force_login(self.user)
    
    def test_create_request(self):
        """Test concierge request creation."""
        request_data = {
            'request_type': 'alcohol',
            'title': 'Dom Pérignon',
            'description': 'Looking for vintage 2012',
            'budget_min': 200.00,
            'budget_max': 500.00,
            'preferred_pickup_date': (date.today() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post(
            '/api/concierge/requests/',
            data=request_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('request_number', data)
        self.assertTrue(data['request_number'].startswith('CR-'))
    
    def test_budget_validation(self):
        """Test budget validation."""
        request_data = {
            'request_type': 'gift',
            'title': 'Test',
            'description': 'Test',
            'budget_min': 500.00,
            'budget_max': 200.00,  # Invalid: max < min
            'preferred_pickup_date': (date.today() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post(
            '/api/concierge/requests/',
            data=request_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_request(self):
        """Test request cancellation."""
        # Create request
        request = ConciergeRequest.objects.create(
            user=self.user,
            request_type='flowers',
            title='Test Flowers',
            description='Test',
            budget_min=50.00,
            budget_max=100.00,
            preferred_pickup_date=date.today() + timedelta(days=5)
        )
        
        # Cancel request
        response = self.client.post(f'/api/concierge/requests/{request.id}/cancel_request/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check status
        request.refresh_from_db()
        self.assertEqual(request.status, 'cancelled')


class ModelValidationTestCase(TestCase):
    """Test model validators."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testvalidation',
            email='testvalidation@test.com',
            password='testpass123'
        )
    
    def test_product_price_validation(self):
        """Test that member_price must be less than price."""
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            product = Product(
                name='Bad Product',
                slug='bad-product',
                category='skincare',
                description='Test',
                short_description='Test',
                price=100.00,
                member_price=150.00,  # Invalid: member > regular
                stock=10
            )
            product.full_clean()
    
    def test_concierge_budget_validation(self):
        """Test budget validation."""
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            request = ConciergeRequest(
                user=self.user,
                request_type='gift',
                title='Test',
                description='Test',
                budget_min=500.00,
                budget_max=200.00,  # Invalid: max < min
                preferred_pickup_date=date.today() + timedelta(days=5)
            )
            request.full_clean()


def run_all_tests():
    """Run all test cases."""
    import sys
    from django.core.management import execute_from_command_line
    
    sys.argv = ['manage.py', 'test', 'tests', '--verbosity=2']
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    run_all_tests()

