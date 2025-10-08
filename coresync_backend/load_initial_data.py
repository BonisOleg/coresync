#!/usr/bin/env python
"""
Load initial data for CoreSync platform.
Creates sample products for Shop app.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Product

def load_shop_products():
    """Load sample products for shop."""
    print("🛍️ Loading Shop Products...")
    
    products = [
        # Skincare
        {
            'name': 'Premium Hyaluronic Serum',
            'slug': 'premium-hyaluronic-serum',
            'category': 'skincare',
            'description': 'Advanced anti-aging serum with pure hyaluronic acid. Deeply hydrates and plumps skin for a youthful glow.',
            'short_description': 'Advanced anti-aging serum',
            'price': 150.00,
            'member_price': 120.00,
            'stock': 25,
            'is_featured': True,
        },
        {
            'name': 'Vitamin C Brightening Cream',
            'slug': 'vitamin-c-brightening-cream',
            'category': 'skincare',
            'description': 'Powerful Vitamin C formula to brighten and even skin tone. Reduces dark spots and hyperpigmentation.',
            'short_description': 'Brightening face cream',
            'price': 120.00,
            'member_price': 96.00,
            'stock': 30,
            'is_featured': True,
        },
        {
            'name': 'Retinol Night Treatment',
            'slug': 'retinol-night-treatment',
            'category': 'skincare',
            'description': 'Clinical-strength retinol treatment for overnight skin renewal. Reduces fine lines and improves texture.',
            'short_description': 'Overnight retinol treatment',
            'price': 180.00,
            'member_price': 144.00,
            'stock': 15,
            'is_featured': False,
        },
        
        # Wellness Tech
        {
            'name': 'Meditation Headband',
            'slug': 'meditation-headband',
            'category': 'wellness',
            'description': 'Smart headband that tracks brainwaves during meditation. Provides real-time feedback for deeper practice.',
            'short_description': 'EEG meditation headband',
            'price': 299.00,
            'member_price': 249.00,
            'stock': 10,
            'is_featured': True,
        },
        {
            'name': 'Infrared Sauna Blanket',
            'slug': 'infrared-sauna-blanket',
            'category': 'wellness',
            'description': 'Portable infrared sauna blanket for at-home detox sessions. Promotes relaxation and muscle recovery.',
            'short_description': 'Portable sauna blanket',
            'price': 499.00,
            'member_price': 399.00,
            'stock': 8,
            'is_featured': True,
        },
        
        # Accessories
        {
            'name': 'Silk Eye Mask',
            'slug': 'silk-eye-mask',
            'category': 'accessories',
            'description': 'Pure mulberry silk eye mask for perfect sleep. Blocks 100% of light while being gentle on skin.',
            'short_description': 'Luxury silk sleep mask',
            'price': 45.00,
            'member_price': 36.00,
            'stock': 50,
            'is_featured': False,
        },
        {
            'name': 'Aromatherapy Diffuser',
            'slug': 'aromatherapy-diffuser',
            'category': 'accessories',
            'description': 'Ultrasonic essential oil diffuser with LED mood lighting. Creates perfect ambiance for relaxation.',
            'short_description': 'Ultrasonic diffuser',
            'price': 89.00,
            'member_price': 71.00,
            'stock': 20,
            'is_featured': False,
        },
        
        # Supplements
        {
            'name': 'Adaptogen Complex',
            'slug': 'adaptogen-complex',
            'category': 'supplements',
            'description': 'Premium adaptogenic blend to support stress resilience and energy. Contains Ashwagandha, Rhodiola, and Reishi.',
            'short_description': 'Stress support supplement',
            'price': 65.00,
            'member_price': 52.00,
            'stock': 40,
            'is_featured': True,
        },
        {
            'name': 'Collagen Beauty Powder',
            'slug': 'collagen-beauty-powder',
            'category': 'supplements',
            'description': 'Marine collagen powder for skin, hair, and nail health. Unflavored and easy to mix.',
            'short_description': 'Marine collagen powder',
            'price': 75.00,
            'member_price': 60.00,
            'stock': 35,
            'is_featured': False,
        },
        {
            'name': 'Omega-3 Triple Strength',
            'slug': 'omega-3-triple-strength',
            'category': 'supplements',
            'description': 'High-potency omega-3 fish oil for heart and brain health. Molecularly distilled for purity.',
            'short_description': 'High-potency omega-3',
            'price': 55.00,
            'member_price': 44.00,
            'stock': 45,
            'is_featured': False,
        },
    ]
    
    created_count = 0
    for product_data in products:
        product, created = Product.objects.get_or_create(
            slug=product_data['slug'],
            defaults=product_data
        )
        if created:
            created_count += 1
            print(f"  ✅ {product.name} - ${product.member_price}")
    
    print(f"\n✅ Loaded {created_count} products (total: {Product.objects.count()})")
    return True

def verify_migrations():
    """Verify all migrations are applied."""
    print("\n🔍 Verifying Migrations...")
    
    from django.db import connection
    
    tables = [
        'shop_products',
        'pickup_orders',
        'order_items',
        'concierge_requests',
    ]
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        db_tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        if table in db_tables:
            print(f"  ✅ Table exists: {table}")
        else:
            print(f"  ❌ Missing table: {table}")
            return False
    
    print("✅ All tables created!\n")
    return True

def test_admin_access():
    """Test that admin panels are registered."""
    print("🔐 Testing Admin Registration...")
    
    from django.contrib import admin
    from shop.models import Product, PickupOrder
    from concierge.models import ConciergeRequest
    
    if admin.site.is_registered(Product):
        print("  ✅ Product admin registered")
    else:
        print("  ❌ Product admin NOT registered")
        return False
    
    if admin.site.is_registered(PickupOrder):
        print("  ✅ PickupOrder admin registered")
    else:
        print("  ❌ PickupOrder admin NOT registered")
        return False
    
    if admin.site.is_registered(ConciergeRequest):
        print("  ✅ ConciergeRequest admin registered")
    else:
        print("  ❌ ConciergeRequest admin NOT registered")
        return False
    
    print("✅ All admin panels registered!\n")
    return True

def main():
    """Run all setup and tests."""
    print("=" * 60)
    print("🚀 CORESYNC - INITIAL DATA & TESTING")
    print("=" * 60)
    
    results = []
    
    # Verify migrations
    results.append(verify_migrations())
    
    # Test admin
    results.append(test_admin_access())
    
    # Load initial data
    results.append(load_shop_products())
    
    # Test functionality
    results.append(test_shop())
    results.append(test_concierge())
    
    print("=" * 60)
    if all(results):
        print("🎉 SETUP COMPLETE - ALL TESTS PASSED!")
        print(f"📊 Products loaded: {Product.objects.count()}")
        print(f"📊 Orders created: {PickupOrder.objects.count()}")
        print(f"📊 Requests created: {ConciergeRequest.objects.count()}")
        print("=" * 60)
        print("\n✅ Ready to test in browser:")
        print("   - Admin: http://localhost:8000/admin/")
        print("   - Shop: http://localhost:8000/shop/")
        print("   - Concierge: http://localhost:8000/concierge/")
        print("   - API: http://localhost:8000/api/shop/products/")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    exit(main())

