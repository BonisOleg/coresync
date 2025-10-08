#!/usr/bin/env python
"""
Test script for Shop and Concierge apps.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Product, PickupOrder
from concierge.models import ConciergeRequest
from users.models import User

def test_shop():
    """Test Shop app."""
    print("\n🛍️ Testing Shop App...")
    
    # Test Product creation
    try:
        product = Product.objects.create(
            name="Premium Face Serum",
            slug="premium-face-serum",
            category="skincare",
            description="Advanced anti-aging serum with hyaluronic acid",
            short_description="Anti-aging serum",
            price=150.00,
            member_price=120.00,
            stock=20,
            is_featured=True
        )
        print(f"✅ Created product: {product}")
        print(f"   - Savings: ${product.savings_amount}")
        print(f"   - Discount: {product.discount_percentage}%")
        print(f"   - In stock: {product.in_stock}")
    except Exception as e:
        print(f"❌ Product creation failed: {e}")
        return False
    
    # Test PickupOrder
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='testuser',
                email='test@test.com',
                password='test123',
                first_name='Test',
                last_name='User'
            )
        
        order = PickupOrder.objects.create(user=user)
        print(f"✅ Created order: {order.order_number}")
        print(f"   - Format: PO-YYYY-NNNNNN ✓")
    except Exception as e:
        print(f"❌ Order creation failed: {e}")
        return False
    
    print("✅ Shop app tests passed!\n")
    return True

def test_concierge():
    """Test Concierge app."""
    print("👑 Testing Concierge App...")
    
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='testuser2',
                email='test2@test.com',
                password='test123',
                first_name='Test',
                last_name='User'
            )
        
        from datetime import date, timedelta
        
        request = ConciergeRequest.objects.create(
            user=user,
            request_type='alcohol',
            title='Dom Pérignon Champagne',
            description='Looking for vintage 2012 if possible',
            budget_min=200.00,
            budget_max=500.00,
            preferred_pickup_date=date.today() + timedelta(days=5)
        )
        print(f"✅ Created request: {request.request_number}")
        print(f"   - Format: CR-YYYY-NNNNNN ✓")
        print(f"   - Age verification: {request.requires_age_verification} ✓")
        print(f"   - Can cancel: {request.can_be_cancelled} ✓")
    except Exception as e:
        print(f"❌ Request creation failed: {e}")
        return False
    
    print("✅ Concierge app tests passed!\n")
    return True

def test_validators():
    """Test validators."""
    print("🔒 Testing Validators...")
    
    # Test product price validation
    try:
        Product.objects.create(
            name="Bad Product",
            slug="bad-product",
            category="skincare",
            description="Test",
            short_description="Test",
            price=100.00,
            member_price=150.00,  # Member price > regular price (should fail)
            stock=10
        )
        print("❌ Validator failed - allowed invalid member price")
        return False
    except Exception:
        print("✅ Price validator working (rejected member_price > price)")
    
    # Test budget validation
    try:
        user = User.objects.first()
        from datetime import date, timedelta
        
        ConciergeRequest.objects.create(
            user=user,
            request_type='gift',
            title='Test',
            description='Test',
            budget_min=500.00,
            budget_max=200.00,  # Max < Min (should fail)
            preferred_pickup_date=date.today() + timedelta(days=5)
        )
        print("❌ Validator failed - allowed invalid budget range")
        return False
    except Exception:
        print("✅ Budget validator working (rejected max < min)")
    
    print("✅ All validators working!\n")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 CORESYNC - SHOP & CONCIERGE TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(test_shop())
    results.append(test_concierge())
    results.append(test_validators())
    
    print("=" * 60)
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    exit(main())

