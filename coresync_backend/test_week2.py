#!/usr/bin/env python3
"""
Week 2 Testing Script
Tests all website pages and functionality.
"""
import requests
from urllib.parse import urljoin

BASE_URL = 'http://localhost:8000'

# All pages to test
PAGES = {
    'Core Pages': [
        ('/', 'Home'),
        ('/private/', 'Private (Couple\'s Spa)'),
        ('/menssuite/', 'Menssuite'),
        ('/membership/', 'Membership'),
        ('/contacts/', 'Contacts'),
        ('/book/', 'Booking Calendar'),
    ],
    'Services': [
        ('/services/', 'Services List'),
    ],
    'Shop & Concierge': [
        ('/shop/', 'Shop'),
        ('/shop/cart/', 'Shopping Cart'),
        ('/concierge/', 'Concierge Request'),
    ],
    'Content Pages': [
        ('/about/', 'About Us'),
        ('/technologies/', 'Technologies'),
    ],
    'Legal Pages': [
        ('/privacy-policy/', 'Privacy Policy'),
        ('/terms/', 'Terms of Service'),
        ('/refund-policy/', 'Refund Policy'),
    ],
    'Auth Pages': [
        ('/login/', 'Login'),
        ('/signup/', 'Signup'),
    ],
    'Dashboard': [
        ('/dashboard/', 'Dashboard Overview'),
        ('/dashboard/bookings/', 'Dashboard Bookings'),
        ('/dashboard/membership/', 'Dashboard Membership'),
        ('/dashboard/profile/', 'Dashboard Profile'),
    ],
}

# API endpoints to test
API_ENDPOINTS = [
    ('/api/health/', 'Health Check'),
    ('/api/services/', 'Services API'),
    ('/api/memberships/plans/', 'Membership Plans API'),
    ('/api/shop/products/', 'Shop Products API'),
    ('/api/shop/products/categories/', 'Shop Categories API'),
]

def test_page(url, name):
    """Test single page."""
    try:
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, timeout=5)
        
        if response.status_code == 200:
            # Check content length
            content_length = len(response.content)
            
            # Check for common elements
            has_title = b'<title>' in response.content
            has_body = b'<body' in response.content or b'<main' in response.content
            
            if content_length < 100:
                print(f"  ⚠️  {name:35} - OK but small ({content_length} bytes)")
                return True
            elif has_title and has_body:
                print(f"  ✅ {name:35} - OK ({content_length} bytes)")
                return True
            else:
                print(f"  ⚠️  {name:35} - OK but incomplete")
                return True
        else:
            print(f"  ❌ {name:35} - Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name:35} - Exception: {str(e)[:40]}")
        return False

def test_api(url, name):
    """Test API endpoint."""
    try:
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, timeout=5)
        
        if response.status_code in [200, 401]:  # 401 is OK for auth-required endpoints
            print(f"  ✅ {name:35} - OK")
            return True
        else:
            print(f"  ❌ {name:35} - Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name:35} - Exception: {str(e)[:40]}")
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("🧪 CORESYNC WEEK 2 - WEBSITE TESTING")
    print("=" * 70)
    print(f"Testing server: {BASE_URL}")
    print("=" * 70)
    
    all_results = []
    
    # Test pages by category
    for category, pages in PAGES.items():
        print(f"\n📄 {category}:")
        for url, name in pages:
            all_results.append(test_page(url, name))
    
    # Test API endpoints
    print(f"\n🔌 API Endpoints:")
    for url, name in API_ENDPOINTS:
        all_results.append(test_api(url, name))
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(all_results)
    total = len(all_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Results: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if percentage == 100:
        print("🎉 ALL TESTS PASSED!")
    elif percentage >= 90:
        print("✅ GOOD - Most tests passed")
    elif percentage >= 75:
        print("⚠️  WARNING - Some tests failed")
    else:
        print("❌ CRITICAL - Many tests failed")
    
    print("=" * 70)
    
    return 0 if percentage >= 90 else 1

if __name__ == '__main__':
    import sys
    
    print("\n💡 Make sure Django server is running:")
    print("   cd coresync_backend && python manage.py runserver\n")
    
    try:
        # Quick check if server is running
        requests.get(BASE_URL, timeout=2)
    except:
        print("❌ Error: Server not responding at", BASE_URL)
        print("   Please start the server first!")
        sys.exit(1)
    
    sys.exit(main())

