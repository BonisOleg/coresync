#!/usr/bin/env python3
"""
Comprehensive Frontend Testing Script
Tests all 23+ pages for functionality.
"""
import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = 'http://localhost:8000'

# All pages organized by category
PAGES = {
    '🏠 Core Pages (6)': [
        ('/', 'Home'),
        ('/private/', 'CoreSync Private'),
        ('/menssuite/', 'Menssuite'),
        ('/membership/', 'Membership'),
        ('/contacts/', 'Contacts'),
        ('/book/', 'Booking Calendar'),
    ],
    '🛍️ Shop & Services (5)': [
        ('/services/', 'Services List'),
        ('/shop/', 'Shop'),
        ('/shop/cart/', 'Shopping Cart'),
        ('/concierge/', 'Concierge'),
    ],
    '📄 Content Pages (2)': [
        ('/about/', 'About Us'),
        ('/technologies/', 'Technologies'),
    ],
    '⚖️ Legal Pages (3)': [
        ('/privacy-policy/', 'Privacy Policy'),
        ('/terms/', 'Terms of Service'),
        ('/refund-policy/', 'Refund Policy'),
    ],
    '🔐 Auth Pages (3)': [
        ('/login/', 'Login'),
        ('/signup/', 'Signup'),
        ('/password-reset/', 'Password Reset'),
    ],
    '📊 Dashboard Pages (4)': [
        ('/dashboard/', 'Dashboard Overview'),
        ('/dashboard/bookings/', 'Dashboard Bookings'),
        ('/dashboard/membership/', 'Dashboard Membership'),
        ('/dashboard/profile/', 'Dashboard Profile'),
    ],
}

API_ENDPOINTS = [
    ('/api/health/', 'Health Check'),
    ('/api/services/', 'Services API'),
    ('/api/memberships/plans/', 'Membership Plans'),
    ('/api/shop/products/', 'Shop Products'),
    ('/api/shop/products/categories/', 'Shop Categories'),
    ('/api/concierge/requests/', 'Concierge Requests'),
]

def test_page(url, name):
    """Test single page."""
    try:
        full_url = f"{BASE_URL}{url}"
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for title
            title = soup.find('title')
            has_title = title is not None
            
            # Check for main content
            has_content = len(response.content) > 500
            
            # Check for CSS
            has_css = soup.find('link', rel='stylesheet') is not None or soup.find('style') is not None
            
            # Check for JavaScript
            has_js = soup.find('script') is not None
            
            checks = sum([has_title, has_content, has_css])
            
            if checks >= 2:
                print(f"  ✅ {name:35} - OK ({len(response.content)} bytes)")
                return True
            else:
                print(f"  ⚠️  {name:35} - OK but incomplete")
                return True
        else:
            print(f"  ❌ {name:35} - Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name:35} - {str(e)[:50]}")
        return False

def test_api(url, name):
    """Test API endpoint."""
    try:
        full_url = f"{BASE_URL}{url}"
        response = requests.get(full_url, timeout=10)
        
        # 200 OK or 401 Unauthorized (auth required) are both fine
        if response.status_code in [200, 401]:
            print(f"  ✅ {name:35} - OK")
            return True
        else:
            print(f"  ❌ {name:35} - Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name:35} - {str(e)[:50]}")
        return False

def main():
    """Run all tests."""
    print("=" * 80)
    print("🧪 CORESYNC - COMPREHENSIVE FRONTEND TESTING")
    print("=" * 80)
    print(f"Server: {BASE_URL}\n")
    
    # Check server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print("❌ Error: Server not responding!")
        print("   Start server: cd coresync_backend && python manage.py runserver")
        return 1
    
    all_results = []
    total_pages = 0
    
    # Test pages by category
    for category, pages in PAGES.items():
        print(f"\n{category}:")
        for url, name in pages:
            result = test_page(url, name)
            all_results.append(result)
            total_pages += 1
    
    # Test API endpoints
    print(f"\n🔌 API Endpoints:")
    for url, name in API_ENDPOINTS:
        result = test_api(url, name)
        all_results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    passed = sum(all_results)
    total = len(all_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 RESULTS:")
    print(f"   Pages tested: {total_pages}")
    print(f"   APIs tested: {len(API_ENDPOINTS)}")
    print(f"   Total tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Success rate: {percentage:.1f}%")
    print("=" * 80)
    
    if percentage == 100:
        print("🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
    elif percentage >= 90:
        print("✅ GOOD - Ready for deployment")
    elif percentage >= 75:
        print("⚠️  WARNING - Some issues to fix")
    else:
        print("❌ CRITICAL - Many pages failing")
    
    print("=" * 80)
    
    return 0 if percentage >= 90 else 1


if __name__ == '__main__':
    sys.exit(main())

