# 🗺️ CORESYNC BACKEND API MAP

## 📋 **ЗАГАЛЬНА ІНФОРМАЦІЯ**

**Base URL:** `https://api.coresync.life/`  
**Authentication:** JWT Bearer Token  
**Content-Type:** `application/json`  
**API Version:** `v1`

---

## 🔐 **AUTHENTICATION ENDPOINTS**

### **POST** `/api/auth/login/`
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "membership_status": "premium",
    "is_member": true
  }
}
```

### **POST** `/api/auth/refresh/`
```json
// Request
{
  "refresh": "jwt_refresh_token"
}

// Response
{
  "access": "new_jwt_access_token"
}
```

### **POST** `/api/auth/register/`
```json
// Request
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}

// Response
{
  "user": {...},
  "access": "jwt_token",
  "refresh": "jwt_refresh_token"
}
```

### **POST** `/api/auth/biometric/register/`
```json
// Request
{
  "face_data": "base64_encoded_face_data",
  "biometric_type": "face_recognition"
}

// Response
{
  "success": true,
  "message": "Biometric data registered successfully"
}
```

### **POST** `/api/auth/biometric/login/`
```json
// Request
{
  "face_data": "base64_encoded_face_data"
}

// Response
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {...}
}
```

---

## 👤 **USER MANAGEMENT**

### **GET** `/api/users/profile/`
**Auth Required:** ✅
```json
// Response
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "membership_status": "premium",
  "membership_plan": {
    "name": "Unlimited",
    "benefits": [...],
    "expires_at": "2024-12-31"
  },
  "biometric_enabled": true,
  "email_notifications": true,
  "sms_notifications": false
}
```

### **PUT** `/api/users/profile/`
**Auth Required:** ✅
```json
// Request
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email_notifications": true,
  "sms_notifications": false
}
```

### **GET** `/api/users/preferences/`
**Auth Required:** ✅
```json
// Response
{
  "default_scene_name": "Swiss Alps",
  "scene_config": {...},
  "favorite_scents": ["lavender", "eucalyptus"],
  "scent_intensity": 3,
  "lighting_type": "warm",
  "lighting_intensity": 70,
  "preferred_temperature": 72.0,
  "music_genre": "ambient",
  "music_volume": 30
}
```

### **PUT** `/api/users/preferences/`
**Auth Required:** ✅

---

## 🏢 **SERVICES & CATEGORIES**

### **GET** `/api/services/categories/`
```json
// Response
[
  {
    "id": 1,
    "name": "Mensuite",
    "slug": "mensuite",
    "description": "Men's Spa services...",
    "image": "/media/categories/mensuite.jpg",
    "featured_technologies": ["smart_mirror", "ai_analyzer"]
  },
  {
    "id": 2,
    "name": "Coresync Private",
    "slug": "coresync-private",
    "description": "Couple's Spa services...",
    "image": "/media/categories/coresync-private.jpg",
    "featured_technologies": ["immersive_screens", "ai_massage"]
  }
]
```

### **GET** `/api/services/`
**Query Parameters:** `?category=mensuite&featured=true`
```json
// Response
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "AI Massage Therapy",
      "slug": "ai-massage-therapy",
      "description": "Advanced AI-guided massage...",
      "short_description": "Personalized massage experience",
      "category": "mensuite",
      "member_price": "150.00",
      "non_member_price": "200.00",
      "duration": 60,
      "max_capacity": 1,
      "requires_appointment": true,
      "member_only": false,
      "featured": true,
      "main_image": "/media/services/ai-massage.jpg",
      "addons": [
        {
          "id": 1,
          "name": "LED Light Therapy",
          "price": "50.00"
        }
      ]
    }
  ]
}
```

### **GET** `/api/services/{slug}/`
```json
// Response
{
  "id": 1,
  "name": "AI Massage Therapy",
  "description": "Full detailed description...",
  "member_price": "150.00",
  "non_member_price": "200.00",
  "duration": 60,
  "gallery_images": ["/media/services/massage1.jpg"],
  "video_url": "https://youtube.com/watch?v=...",
  "addons": [...],
  "available_programs": [
    {
      "name": "Deep Relaxation",
      "description": "..."
    },
    {
      "name": "Athletic Recovery", 
      "description": "..."
    }
  ]
}
```

### **GET** `/api/services/mensuite/`
**Shortcut для послуг Mensuite**

### **GET** `/api/services/coresync-private/`
**Shortcut для послуг Coresync Private**

---

## 💎 **MEMBERSHIP MANAGEMENT**

### **GET** `/api/memberships/plans/`
```json
// Response
[
  {
    "id": 1,
    "name": "Mensuite",
    "slug": "mensuite",
    "description": "Men's Spa access...",
    "price": "199.00",
    "duration_months": 12,
    "benefits": [
      "Access to all men's services",
      "20% discount on services",
      "Priority booking"
    ],
    "discount_percentage": 20,
    "mensuite_access": true,
    "coresync_private_access": false,
    "iot_control_access": true,
    "priority_booking": true,
    "monthly_service_credits": 2,
    "guest_passes": 1,
    "featured": false,
    "color_scheme": "#1a1a1a",
    "icon": "fa-male"
  },
  {
    "id": 2,
    "name": "Coresync Private",
    "slug": "coresync-private",
    "price": "299.00",
    "coresync_private_access": true,
    "featured": false
  },
  {
    "id": 3,
    "name": "Unlimited",
    "slug": "unlimited",
    "price": "399.00",
    "mensuite_access": true,
    "coresync_private_access": true,
    "featured": true
  }
]
```

### **GET** `/api/memberships/my-membership/`
**Auth Required:** ✅
```json
// Response
{
  "id": 1,
  "plan": {
    "name": "Unlimited",
    "benefits": [...]
  },
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "status": "active",
  "services_used_this_month": 3,
  "guest_passes_used": 0,
  "days_remaining": 45,
  "auto_renew": true,
  "can_use_service_credit": true
}
```

### **POST** `/api/memberships/upgrade/`
**Auth Required:** ✅
```json
// Request
{
  "plan_id": 3,
  "payment_method": "stripe_card"
}

// Response
{
  "success": true,
  "membership": {...},
  "payment": {...}
}
```

---

## 📅 **BOOKING SYSTEM**

### **GET** `/api/bookings/availability/`
**Query:** `?date=2024-01-15&service_id=1&duration=60`
```json
// Response
{
  "date": "2024-01-15",
  "available_slots": [
    {
      "start_time": "09:00",
      "end_time": "10:00",
      "is_priority": true,
      "room_id": 1,
      "room_name": "Mensuite Room A"
    },
    {
      "start_time": "14:00", 
      "end_time": "15:00",
      "is_priority": false,
      "room_id": 2,
      "room_name": "Mensuite Room B"
    }
  ]
}
```

### **POST** `/api/bookings/create/`
**Auth Required:** ✅
```json
// Request
{
  "service_id": 1,
  "date": "2024-01-15",
  "start_time": "14:00",
  "room_id": 1,
  "addons": [1, 3],
  "special_requests": "Prefer warm towels",
  "ai_program": "deep_relaxation",
  "scene_name": "Swiss Alps"
}

// Response
{
  "id": 123,
  "booking_reference": "CS-2024-123",
  "service": {...},
  "date": "2024-01-15",
  "start_time": "14:00",
  "end_time": "15:00",
  "total_amount": "200.00",
  "payment_status": "pending",
  "confirmation_sent": true
}
```

### **GET** `/api/bookings/my-bookings/`
**Auth Required:** ✅
```json
// Response
{
  "upcoming": [
    {
      "id": 123,
      "service": "AI Massage Therapy",
      "date": "2024-01-15",
      "start_time": "14:00",
      "status": "confirmed",
      "can_cancel": true,
      "can_reschedule": true
    }
  ],
  "past": [...]
}
```

### **PUT** `/api/bookings/{id}/cancel/`
**Auth Required:** ✅

### **PUT** `/api/bookings/{id}/reschedule/`
**Auth Required:** ✅

---

## 🤖 **IOT CONTROL SYSTEM**

### **GET** `/api/iot/devices/`
**Auth Required:** ✅
**Query:** `?location=mensuite_main&device_type=lighting`
```json
// Response
[
  {
    "id": 1,
    "name": "Main Lighting System",
    "device_type": "lighting",
    "location": "mensuite_main",
    "current_status": {
      "brightness": 70,
      "color": "#ff9500",
      "mode": "warm"
    },
    "is_online": true,
    "min_value": 0,
    "max_value": 100,
    "default_value": 50
  }
]
```

### **POST** `/api/iot/devices/{id}/control/`
**Auth Required:** ✅
```json
// Request
{
  "action": "set_brightness",
  "value": 80,
  "duration": 300
}

// Response
{
  "success": true,
  "device_status": {...},
  "message": "Lighting adjusted successfully"
}
```

### **GET** `/api/iot/scenes/`
**Auth Required:** ✅
```json
// Response
[
  {
    "id": 1,
    "name": "Swiss Alps",
    "description": "Mountain relaxation scene",
    "scene_type": "preset",
    "location": "coresync_suite",
    "device_settings": {
      "lighting": {"brightness": 60, "color": "#87CEEB"},
      "scent": {"type": "alpine", "intensity": 3},
      "temperature": 70,
      "music": {"playlist": "nature_sounds", "volume": 25}
    },
    "usage_count": 245,
    "is_public": true
  }
]
```

### **POST** `/api/iot/scenes/create/`
**Auth Required:** ✅
```json
// Request
{
  "name": "My Custom Scene",
  "description": "Personal relaxation setup",
  "location": "coresync_suite",
  "device_settings": {...}
}
```

### **POST** `/api/iot/scenes/{id}/activate/`
**Auth Required:** ✅

---

## 🛍️ **SHOP & CONCIERGE**

### **GET** `/api/shop/products/`
**Query:** `?category=skincare&featured=true`
```json
// Response
{
  "results": [
    {
      "id": 1,
      "name": "Premium Face Serum",
      "description": "Anti-aging serum...",
      "price": "89.00",
      "category": "skincare",
      "image": "/media/products/serum.jpg",
      "in_stock": true,
      "featured": true
    }
  ]
}
```

### **POST** `/api/shop/purchase/`
**Auth Required:** ✅
```json
// Request
{
  "product_id": 1,
  "quantity": 2,
  "pickup_date": "2024-01-20"
}

// Response
{
  "order_id": "ORD-2024-456",
  "total_amount": "178.00",
  "pickup_ready": "2024-01-20",
  "payment_status": "charged"
}
```

### **POST** `/api/concierge/request/`
**Auth Required:** ✅
```json
// Request
{
  "item_description": "Japanese whisky - Hibiki 21",
  "item_url": "https://example.com/product",
  "budget": "400.00",
  "needed_by": "2024-01-20",
  "special_instructions": "For anniversary celebration"
}

// Response
{
  "request_id": "CON-2024-789",
  "status": "received",
  "estimated_fulfillment": "2024-01-18",
  "message": "We'll source this item for you"
}
```

### **GET** `/api/concierge/my-requests/`
**Auth Required:** ✅

---

## 💳 **PAYMENTS & STRIPE**

### **POST** `/api/payments/create-intent/`
**Auth Required:** ✅
```json
// Request
{
  "amount": "200.00",
  "currency": "usd",
  "payment_type": "service",
  "booking_id": 123,
  "save_card": true
}

// Response
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx",
  "amount": 20000,
  "currency": "usd"
}
```

### **POST** `/api/payments/confirm/`
**Auth Required:** ✅
```json
// Request
{
  "payment_intent_id": "pi_xxx",
  "payment_method_id": "pm_xxx"
}

// Response
{
  "status": "succeeded",
  "payment": {...},
  "receipt_url": "https://..."
}
```

### **GET** `/api/payments/saved-cards/`
**Auth Required:** ✅
```json
// Response
[
  {
    "id": "pm_xxx",
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025,
    "is_default": true
  }
]
```

### **POST** `/api/payments/webhook/stripe/`
**Stripe webhook endpoint**

---

## 📊 **AI RECOMMENDATIONS**

### **GET** `/api/ai/recommendations/`
**Auth Required:** ✅
```json
// Response
{
  "last_service": {
    "name": "Facial Treatment",
    "date": "2024-01-01",
    "days_ago": 14
  },
  "recommendations": [
    {
      "type": "service",
      "service_id": 5,
      "service_name": "LED Light Therapy",
      "reason": "Based on your skin analysis",
      "priority": "high",
      "suggested_date": "2024-01-20"
    },
    {
      "type": "reminder",
      "message": "You haven't visited in 3 weeks - time for maintenance?",
      "action": "book_massage"
    }
  ],
  "optimal_frequency": {
    "service_type": "facial",
    "recommended_interval_days": 21
  }
}
```

### **POST** `/api/ai/feedback/`
**Auth Required:** ✅
```json
// Request
{
  "recommendation_id": 123,
  "action": "accepted", // or "declined"
  "feedback": "Great suggestion!"
}
```

---

## 📈 **ANALYTICS & HISTORY**

### **GET** `/api/analytics/service-history/`
**Auth Required:** ✅
```json
// Response
{
  "total_visits": 25,
  "total_spent": "3750.00",
  "favorite_service": "AI Massage Therapy",
  "last_visit": "2024-01-01",
  "services": [
    {
      "id": 1,
      "service_name": "AI Massage Therapy",
      "date": "2024-01-01",
      "price_paid": "150.00",
      "rating": 5,
      "addons": ["LED Light Therapy"],
      "staff_notes": "Preferred medium pressure"
    }
  ],
  "monthly_stats": {
    "january_2024": {
      "visits": 3,
      "spent": "450.00"
    }
  }
}
```

### **POST** `/api/analytics/rate-service/`
**Auth Required:** ✅
```json
// Request
{
  "service_history_id": 123,
  "rating": 5,
  "feedback": "Excellent experience!"
}
```

---

## 💰 **INVESTMENT PORTAL**

### **GET** `/api/investment/opportunities/`
**Auth Required:** ✅ + **Investment Access**
```json
// Response
[
  {
    "id": 1,
    "title": "CoreSync NYC Expansion",
    "description": "New location in Manhattan",
    "minimum_investment": "50000.00",
    "expected_roi": "15-20%",
    "timeline": "18-24 months",
    "documents": [
      {
        "name": "Investment Prospectus",
        "url": "/secure/documents/prospectus.pdf",
        "type": "pdf"
      }
    ],
    "status": "open"
  }
]
```

### **GET** `/api/investment/documents/{id}/`
**Auth Required:** ✅ + **Investment Access**

### **POST** `/api/investment/express-interest/`
**Auth Required:** ✅
```json
// Request
{
  "opportunity_id": 1,
  "investment_amount": "75000.00",
  "contact_method": "email",
  "message": "Interested in learning more"
}
```

---

## 📝 **FORMS & SUBMISSIONS**

### **POST** `/api/forms/contact/`
```json
// Request
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "message": "Interested in services",
  "source": "website"
}

// Response
{
  "success": true,
  "submission_id": "CONT-2024-001",
  "message": "Thank you for your inquiry"
}
```

### **POST** `/api/forms/membership-inquiry/`
```json
// Request
{
  "first_name": "John",
  "last_name": "Doe", 
  "email": "john@example.com",
  "phone": "+1234567890",
  "interested_plan": "unlimited",
  "interest_level": "high",
  "preferred_services": ["massage", "facial"],
  "how_heard_about_us": "Google search"
}
```

### **POST** `/api/forms/newsletter/`
```json
// Request
{
  "email": "john@example.com",
  "first_name": "John",
  "marketing_emails": true,
  "service_updates": true,
  "special_offers": true
}
```

---

## 🔔 **NOTIFICATIONS**

### **GET** `/api/notifications/`
**Auth Required:** ✅
```json
// Response
[
  {
    "id": 1,
    "type": "booking_reminder",
    "title": "Appointment Tomorrow",
    "message": "Your AI Massage appointment is tomorrow at 2:00 PM",
    "created_at": "2024-01-14T10:00:00Z",
    "read": false,
    "action_url": "/bookings/123"
  }
]
```

### **POST** `/api/notifications/{id}/mark-read/`
**Auth Required:** ✅

### **PUT** `/api/notifications/preferences/`
**Auth Required:** ✅
```json
// Request
{
  "push_notifications": true,
  "email_notifications": true,
  "sms_notifications": false,
  "booking_reminders": true,
  "promotional_offers": false
}
```

---

## 🔒 **ERROR HANDLING**

### **Standard Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required"],
      "phone": ["Invalid phone number format"]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_abc123"
}
```

### **HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Server Error

---

## 🔄 **WEBSOCKET CONNECTIONS**

### **Real-time IoT Updates:**
```javascript
// Connect
ws://api.coresync.life/ws/iot/room-123/

// Messages
{
  "type": "device_status_update",
  "device_id": 1,
  "status": {
    "brightness": 75,
    "temperature": 72
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### **Booking Updates:**
```javascript
// Connect  
ws://api.coresync.life/ws/bookings/

// Messages
{
  "type": "booking_confirmed", 
  "booking_id": 123,
  "message": "Your appointment has been confirmed"
}
```

---

## 📱 **MOBILE APP SPECIFIC**

### **Face Recognition Check-in:**
```json
// POST /api/mobile/checkin/
{
  "face_data": "base64_image",
  "location": "mensuite_entrance"
}

// Response
{
  "success": true,
  "user": {...},
  "upcoming_booking": {...},
  "room_ready": true,
  "welcome_message": "Welcome back, John!"
}
```

### **Equipment Sync:**
```json
// POST /api/mobile/sync-preferences/
{
  "booking_id": 123,
  "preferences": {
    "scene": "swiss_alps",
    "lighting": {...},
    "temperature": 72,
    "music": {...}
  }
}
```

---

## 📊 **ADMIN ENDPOINTS**

### **Dashboard Stats:**
```json
// GET /api/admin/dashboard/
{
  "today": {
    "bookings": 25,
    "revenue": "3750.00",
    "new_members": 3,
    "active_sessions": 8
  },
  "devices": {
    "online": 45,
    "offline": 2,
    "maintenance": 1
  },
  "recent_activity": [...]
}
```

---

## 🔗 **EXTERNAL INTEGRATIONS**

### **QuickBooks Sync:**
- Automatic payment sync
- Customer data sync
- Service revenue tracking
- Tax reporting integration

### **Stripe Integration:**
- Payment processing
- Subscription management
- Webhook handling
- Card storage

### **Email Service:**
- Booking confirmations
- Membership notifications
- Marketing campaigns
- Transactional emails

---

## 🚀 **DEPLOYMENT INFO**

**Production:** `https://api.coresync.life/`  
**Staging:** `https://staging-api.coresync.life/`  
**Development:** `http://localhost:8000/`

**API Documentation:** `https://api.coresync.life/docs/`  
**Admin Panel:** `https://api.coresync.life/admin/`

---

## 📝 **NOTES FOR FRONTEND DEVELOPERS**

1. **Authentication:** Include `Authorization: Bearer {token}` header
2. **Error Handling:** Always check for error responses
3. **Rate Limiting:** Implement exponential backoff
4. **WebSockets:** Use for real-time IoT updates
5. **File Uploads:** Use multipart/form-data for images
6. **Pagination:** Check `next`/`previous` links
7. **Caching:** Cache static data (services, categories)
8. **Offline:** Store critical data locally

**Contact Backend Team:** `backend@coresync.life`
