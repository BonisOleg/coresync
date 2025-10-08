# 🚀 CORESYNC - SENIOR DEVELOPMENT PLAN TO 99%

**Створено**: October 8, 2025  
**Статус**: Дороблення до production-ready  
**Мета**: Довести проект до 99% готовності, залишивши лише відео контент та IoT налаштування

---

## 📊 EXECUTIVE SUMMARY

**Поточний стан**: 75% готовності  
**Цільовий стан**: 99% готовності  
**Залишиться**: Тільки відео контент + IoT фінальне налаштування + App Store/Play Store публікація

**Ключові принципи**:
- ✅ Максимальне використання наявного коду
- ✅ Уникнення дублювань та конфліктів
- ✅ Відсутність inline стилів (вже чисто!)
- ✅ Мінімізація !important (тільки 14 випадків)
- ✅ Clean Architecture для Flutter app
- ✅ Production-ready код з першого разу

---

## 🎯 PHASE 1: WEB-SITE COMPLETION (Тиждень 1-2)

### **PRIORITY A: Critical Missing Pages (Days 1-5)**

#### 1.1 Shop/Retail Page - `/shop/`
**Файл**: `coresync_backend/templates/shop/index.html`

**Структура** (використати наявний код з `index.html` + `services/list.html`):
```html
<!-- Base: templates/base.html -->
<!-- Hero Section: використати з index.html -->
<!-- Product Grid: адаптувати з services/list.html -->
```

**Компоненти**:
- **Hero Section**: "Curated Spa Products" (з index.html)
- **Categories Grid**: Skincare, Wellness Tech, Accessories, Supplements
- **Product Cards**: З pricing, "Add to Pickup List"
- **Pickup Notice**: "Available for pickup on your next visit"
- **Filter & Sort**: За категорією, ціною

**CSS**: Використати наявні класи:
- `.hero-section` (є в styles.css)
- `.service-card` → `.product-card` (адаптувати)
- `.btn-primary`, `.btn-secondary` (є)

**JavaScript**: Адаптувати з `booking.js`:
- LocalStorage для pickup list
- Add to cart functionality
- Filter/sort logic

**URL**: Додати в `config/urls.py`:
```python
path('shop/', TemplateView.as_view(template_name='shop/index.html'), name='shop'),
path('shop/cart/', TemplateView.as_view(template_name='shop/cart.html'), name='shop_cart'),
```

---

#### 1.2 Concierge Service Page - `/concierge/`
**Файл**: `coresync_backend/templates/concierge/request.html`

**Структура** (використати форму з `contacts.html`):
```html
<!-- Base: templates/base.html -->
<!-- Form: адаптувати з contacts.html -->
<!-- Request Types: Select dropdown -->
```

**Компоненти**:
- **Hero Section**: "Personal Concierge Service"
- **Request Form**:
  - Request Type (dropdown): Alcohol, Flowers, Food, Luxury Items, Other
  - Product Link (URL input)
  - Description (textarea)
  - Budget Range (select)
  - Preferred Pickup Date (date picker)
- **Status Tracking**: "Your Requests" (для членів)
- **Terms**: "Available for Premium & Unlimited members only"

**CSS**: Використати:
- `.contact-form` → `.concierge-form`
- `.form-group`, `.form-input`, `.form-textarea` (є)
- `.status-badge` (новий, на основі `.membership-badge`)

**API Integration**: Створити API endpoint
```python
# concierge/views.py
class ConciergeRequestViewSet(viewsets.ModelViewSet):
    # Similar to booking_views.py
```

**URL**: Додати в `config/urls.py`:
```python
path('concierge/', TemplateView.as_view(template_name='concierge/request.html'), name='concierge'),
path('api/concierge/', include('concierge.urls')),
```

---

#### 1.3 My Membership Detail Page - `/dashboard/membership-detail/`
**Файл**: `coresync_backend/templates/dashboard/membership_detail.html`

**Структура** (розширити `dashboard/membership.html`):
```html
<!-- Base: templates/dashboard/base_dashboard.html -->
<!-- Stats Cards: з dashboard/overview.html -->
<!-- Benefits List: з membership.html -->
```

**Секції**:
1. **Current Plan Overview**
   - Plan name + badge
   - Price per month
   - Renewal date
   - Cancel/Upgrade buttons

2. **Benefits & Perks**
   - Priority booking status
   - Included services count
   - Exclusive perks list
   - Birthday benefit (if applicable)

3. **Usage Analytics**
   - Services used this month
   - Savings vs non-member prices
   - Visit frequency graph
   - Most booked services

4. **Upgrade Path**
   - "Upgrade to Premium" card
   - Savings calculator
   - Feature comparison

**JavaScript**: Використати `dashboard.js`:
```javascript
// Розширити існуючий DashboardAPI class
async getMembershipDetails() {
    return this.request('/api/memberships/my-plan/');
}
```

**URL**: Вже є в `config/urls.py`, просто створити template

---

#### 1.4 Service Detail Page - `/services/<slug>/`
**Файл**: Покращити `coresync_backend/templates/services/detail.html`

**Наразі є базовий template**, потрібно додати:

**Секції для додавання**:
1. **Hero Image Carousel** (з index.html gallery logic)
2. **Pricing Tiers**:
   - Non-member price
   - Base member price
   - Premium member price
   - Unlimited included
3. **Available Add-ons**:
   - LED Light Therapy
   - Oxygen Treatment
   - Extended session
4. **Duration & Details**:
   - Session length
   - What to expect
   - Preparation tips
5. **Book Now Section**:
   - Calendar integration (з booking_calendar.html)
   - Add-ons selection
   - Instant booking

**JavaScript**: Інтегрувати з `booking.js`:
```javascript
// Add to existing booking.js
function bookServiceFromDetail(serviceId, addons = []) {
    // Use existing booking logic
}
```

---

#### 1.5 Legal Pages (Days 6-7)

##### 1.5.1 Privacy Policy - `/privacy-policy/`
**Файл**: `coresync_backend/templates/legal/privacy_policy.html`

**Секції**:
1. Information Collection
2. Biometric Data Handling (Face Recognition)
3. Payment Information Security
4. Cookie Policy
5. Third-party Services (Stripe, QuickBooks)
6. User Rights (GDPR/CCPA)
7. Data Retention
8. Contact Information

**Template Structure**:
```html
<!-- Base: templates/base.html -->
<div class="legal-page">
    <section class="legal-hero">
        <h1>Privacy Policy</h1>
        <p class="last-updated">Last Updated: October 8, 2025</p>
    </section>
    <section class="legal-content">
        <!-- Використати typography з about.html -->
    </section>
</div>
```

##### 1.5.2 Terms of Service - `/terms/`
**Файл**: `coresync_backend/templates/legal/terms.html`

**Секції**:
1. Membership Terms
2. Service Booking Rules
3. Cancellation Policy
4. Member Conduct
5. Facility Rules
6. Intellectual Property
7. Limitation of Liability
8. Dispute Resolution

##### 1.5.3 Refund Policy - `/refund-policy/`
**Файл**: `coresync_backend/templates/legal/refund_policy.html`

**Секції**:
1. Membership Refunds
2. Service Cancellation Rules
3. Timeline (2-3 months for members)
4. Special Circumstances
5. Processing Time
6. Contact for Refund Requests

**CSS для всіх legal pages**: Новий файл
```css
/* legal.css - базувати на existing styles */
.legal-page {
    /* Use container, typography from styles.css */
}
```

**URL**: Додати в `config/urls.py`:
```python
path('privacy-policy/', TemplateView.as_view(template_name='legal/privacy_policy.html'), name='privacy_policy'),
path('terms/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
path('refund-policy/', TemplateView.as_view(template_name='legal/refund_policy.html'), name='refund_policy'),
```

---

### **PRIORITY B: Enhanced Existing Pages (Days 8-10)**

#### 2.1 About Us Page - Розширити `/about/`
**Файл**: `coresync_backend/templates/pages/about.html` (вже є)

**Додати секції**:
1. **Founder's Story**
   - Personal journey
   - Vision for CoreSync
   - Photo/video

2. **Team Members**
   - Key team cards
   - Roles and expertise
   - Photos

3. **Timeline & Milestones**
   - Founding date
   - Location opening
   - Awards/recognition

4. **Mission & Values**
   - Core values list
   - Community commitment
   - Sustainability efforts

**Використати наявний код**:
- `.about-section` (є)
- `.team-grid` (створити на базі `.service-grid`)
- `.timeline` (нова, але проста CSS)

---

#### 2.2 Technologies Page - Розширити `/technologies/`
**Файл**: `coresync_backend/templates/pages/technologies.html` (вже є)

**Додати детальні секції для кожного пристрою**:

1. **AI Massage Bed**
   - Specs and features
   - Available programs
   - Benefits
   - Demo video placeholder
   - "Book Now" CTA

2. **Meditation Pods**
   - Technology details
   - Breathwork programs
   - Sensory features
   - Booking options

3. **Oxygen Dome**
   - Health benefits
   - Safety features
   - Session details

4. **Immersive 4D Screens**
   - Resolution specs
   - Available scenes
   - Custom content upload
   - Sound system

5. **Smart Mirror**
   - Features
   - Personalization options

**JavaScript**: Додати tabs для переключення між пристроями
```javascript
// technologies.js - новий файл
class TechnologiesPage {
    constructor() {
        this.initTabs();
        this.initVideoPlaceholders();
    }
    // Use patterns from existing JS files
}
```

---

### **PRIORITY C: Code Cleanup & Optimization (Days 11-12)**

#### 3.1 Remove Remaining !important
**Файли**: `styles.css` (8 випадків), `membership.css` (6 випадків)

**Дії**:
1. Знайти всі 14 випадки `!important`
2. Перевірити, чому вони потрібні
3. Виправити специфічність селекторів
4. Видалити `!important`

```bash
# Знайти всі !important
grep -r "!important" coresync_backend/static/css/

# Для кожного:
# 1. Знайти конфлікт
# 2. Збільшити специфічність правильного селектора
# 3. Видалити !important
```

#### 3.2 Consolidate Duplicate Code
**Файли для перевірки**:
- `static/js/booking.js` + `static/js/dashboard.js` (DashboardAPI duplicate?)
- CSS media queries (багато дублювань?)

**Створити**:
- `static/js/shared/api-client.js` - Single API client для всіх
- `static/js/shared/utils.js` - Shared utilities

**Refactor приклад**:
```javascript
// Before (duplicate in booking.js and dashboard.js):
class DashboardAPI { ... }

// After (shared/api-client.js):
class CoreSyncAPI {
    constructor(baseURL) { ... }
    // All API methods here
}

// booking.js:
import { CoreSyncAPI } from './shared/api-client.js';
const api = new CoreSyncAPI('/api');
```

#### 3.3 CSS Organization
**Поточна структура**:
```
static/css/
├── styles.css (1554 lines!)
├── membership.css
├── responsive.css
├── dashboard.css
├── animations.css
```

**Оптимізувати**:
```
static/css/
├── 1-base/
│   ├── reset.css
│   ├── typography.css
│   └── variables.css
├── 2-layout/
│   ├── header.css
│   ├── footer.css
│   ├── grid.css
│   └── responsive.css
├── 3-components/
│   ├── buttons.css
│   ├── cards.css
│   ├── forms.css
│   └── modals.css
├── 4-pages/
│   ├── home.css
│   ├── membership.css
│   ├── dashboard.css
│   └── legal.css
└── 5-utilities/
    ├── animations.css
    └── helpers.css
```

**BUT**: Це можна зробити пізніше - не критично!

---

### **PRIORITY D: Backend API Completion (Days 13-14)**

#### 4.1 Створити Missing API Apps

##### 4.1.1 Concierge App
```bash
cd coresync_backend
python manage.py startapp concierge
```

**Файли для створення**:
```
concierge/
├── __init__.py
├── models.py         # ConciergeRequest model
├── serializers.py    # API serializers
├── views.py          # ViewSets
├── urls.py           # API routes
└── admin.py          # Admin interface
```

**models.py** (база на services/booking_models.py):
```python
class ConciergeRequest(models.Model):
    REQUEST_TYPES = (
        ('alcohol', 'Premium Alcohol'),
        ('flowers', 'Fresh Flowers'),
        ('food', 'Gourmet Food'),
        ('luxury', 'Luxury Items'),
        ('other', 'Other'),
    )
    
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    product_link = models.URLField(blank=True)
    description = models.TextField()
    budget_range = models.DecimalField(max_digits=10, decimal_places=2)
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
```

##### 4.1.2 Shop App
```bash
python manage.py startapp shop
```

**Models**:
```python
# shop/models.py
class Product(models.Model):
    CATEGORIES = (
        ('skincare', 'Skincare'),
        ('wellness', 'Wellness Tech'),
        ('accessories', 'Accessories'),
        ('supplements', 'Supplements'),
    )
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    member_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

class PickupOrder(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

#### 4.2 Update Database
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if not exists
python manage.py createsuperuser

# Load initial data
python manage.py loaddata initial_services.json
python manage.py loaddata initial_memberships.json
```

#### 4.3 Add API URLs
**File**: `config/urls.py`
```python
urlpatterns = [
    # ... existing ...
    path('', include('concierge.urls')),  # Concierge API
    path('', include('shop.urls')),       # Shop API
]
```

---

## 🎯 PHASE 2: FLUTTER MOBILE APP COMPLETION (Тиждень 3-4)

### **PRIORITY A: Core Features Implementation (Days 15-21)**

#### 5.1 Face Recognition Login (Days 15-16)

**Використати наявну структуру**:
- `features/auth/domain/usecases/face_recognition_usecase.dart` (вже є!)
- `features/auth/presentation/pages/face_registration_page.dart` (вже є!)

**Package вже є**: `google_mlkit_face_detection: ^0.9.0`

**Реалізувати в існуючих файлах**:

**File**: `lib/features/auth/domain/usecases/face_recognition_usecase.dart`
```dart
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:camera/camera.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class FaceRecognitionUseCase {
  final FaceDetector _faceDetector;
  final FlutterSecureStorage _secureStorage;
  
  FaceRecognitionUseCase()
      : _faceDetector = FaceDetector(
          options: FaceDetectorOptions(
            enableClassification: true,
            enableLandmarks: true,
            enableTracking: true,
            performanceMode: FaceDetectorMode.accurate,
          ),
        ),
        _secureStorage = const FlutterSecureStorage();

  // Registration: Save face template
  Future<bool> registerFace(CameraImage image) async {
    try {
      final inputImage = _convertToInputImage(image);
      final faces = await _faceDetector.processImage(inputImage);
      
      if (faces.isEmpty || faces.length > 1) {
        return false; // Need exactly one face
      }
      
      final face = faces.first;
      final faceTemplate = _extractFaceTemplate(face);
      
      // Save to secure storage
      await _secureStorage.write(
        key: 'face_template',
        value: faceTemplate,
      );
      
      return true;
    } catch (e) {
      return false;
    }
  }
  
  // Authentication: Compare face with stored template
  Future<bool> authenticateFace(CameraImage image) async {
    try {
      final storedTemplate = await _secureStorage.read(key: 'face_template');
      if (storedTemplate == null) return false;
      
      final inputImage = _convertToInputImage(image);
      final faces = await _faceDetector.processImage(inputImage);
      
      if (faces.isEmpty) return false;
      
      final face = faces.first;
      final currentTemplate = _extractFaceTemplate(face);
      
      // Compare templates (simple distance comparison)
      final similarity = _compareFaceTemplates(storedTemplate, currentTemplate);
      
      return similarity > 0.85; // 85% match threshold
    } catch (e) {
      return false;
    }
  }
  
  // Helper methods
  InputImage _convertToInputImage(CameraImage image) {
    // Implementation for camera image to InputImage conversion
    // ...
  }
  
  String _extractFaceTemplate(Face face) {
    // Extract face landmarks and create template
    final landmarks = face.landmarks;
    final leftEye = landmarks[FaceLandmarkType.leftEye];
    final rightEye = landmarks[FaceLandmarkType.rightEye];
    final nose = landmarks[FaceLandmarkType.noseBase];
    // ... extract all landmarks
    
    // Create template string (in production use proper encoding)
    return 'template_data';
  }
  
  double _compareFaceTemplates(String template1, String template2) {
    // Implement template comparison
    // In production use proper face recognition algorithm
    return 0.9; // Placeholder
  }
}
```

**File**: `lib/features/auth/presentation/pages/face_registration_page.dart`
```dart
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../../domain/usecases/face_recognition_usecase.dart';

class FaceRegistrationPage extends StatefulWidget {
  const FaceRegistrationPage({super.key});
  
  @override
  State<FaceRegistrationPage> createState() => _FaceRegistrationPageState();
}

class _FaceRegistrationPageState extends State<FaceRegistrationPage> {
  CameraController? _cameraController;
  final FaceRecognitionUseCase _faceRecognition = FaceRecognitionUseCase();
  bool _isProcessing = false;
  String _statusMessage = 'Position your face in the circle';
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    final frontCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front,
    );
    
    _cameraController = CameraController(
      frontCamera,
      ResolutionPreset.high,
      enableAudio: false,
    );
    
    await _cameraController!.initialize();
    await _cameraController!.startImageStream(_processCameraImage);
    
    if (mounted) setState(() {});
  }
  
  void _processCameraImage(CameraImage image) async {
    if (_isProcessing) return;
    
    _isProcessing = true;
    
    final success = await _faceRecognition.registerFace(image);
    
    if (success) {
      setState(() => _statusMessage = 'Face registered successfully!');
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) Navigator.of(context).pop(true);
    } else {
      setState(() => _statusMessage = 'Face not detected. Try again.');
    }
    
    _isProcessing = false;
  }
  
  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('Register Your Face'),
        backgroundColor: Colors.transparent,
      ),
      body: Stack(
        children: [
          // Camera preview
          Positioned.fill(
            child: CameraPreview(_cameraController!),
          ),
          
          // Face oval overlay
          Center(
            child: Container(
              width: 300,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: Colors.white,
                  width: 3,
                ),
              ),
            ),
          ),
          
          // Status message
          Positioned(
            bottom: 100,
            left: 0,
            right: 0,
            child: Text(
              _statusMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }
}
```

**Integration Point**: Update login page to use face recognition
```dart
// lib/features/auth/presentation/pages/login_page.dart
// Add "Login with Face" button
```

---

#### 5.2 Real-time Booking (Days 17-18)

**File**: `lib/features/booking/data/booking_repository.dart` (створити)
```dart
import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class BookingRepository {
  final ApiClient _apiClient;
  
  BookingRepository(this._apiClient);
  
  // Get available time slots
  Future<List<TimeSlot>> getAvailableSlots({
    required DateTime date,
    required String serviceId,
  }) async {
    final response = await _apiClient.get(
      '/api/bookings/available-slots/',
      queryParameters: {
        'date': date.toIso8601String(),
        'service': serviceId,
      },
    );
    
    return (response.data as List)
        .map((slot) => TimeSlot.fromJson(slot))
        .toList();
  }
  
  // Create booking
  Future<Booking> createBooking({
    required String serviceId,
    required DateTime dateTime,
    List<String> addonIds = const [],
  }) async {
    final response = await _apiClient.post(
      '/api/bookings/',
      data: {
        'service': serviceId,
        'datetime': dateTime.toIso8601String(),
        'addons': addonIds,
      },
    );
    
    return Booking.fromJson(response.data);
  }
  
  // Cancel booking
  Future<void> cancelBooking(String bookingId) async {
    await _apiClient.delete('/api/bookings/$bookingId/');
  }
  
  // Get my bookings
  Future<List<Booking>> getMyBookings() async {
    final response = await _apiClient.get('/api/bookings/my-bookings/');
    return (response.data as List)
        .map((booking) => Booking.fromJson(booking))
        .toList();
  }
}
```

**Update existing page**: `lib/features/booking/presentation/pages/booking_page.dart`
- Add real API integration
- Replace mock data with real API calls
- Add loading states
- Add error handling

---

#### 5.3 IoT Device Control (Days 19-20)

**File**: `lib/features/iot/data/iot_repository.dart` (створити)
```dart
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/network/api_client.dart';

class IoTRepository {
  final ApiClient _apiClient;
  WebSocketChannel? _wsChannel;
  
  IoTRepository(this._apiClient);
  
  // Connect to WebSocket for real-time updates
  Stream<IoTUpdate> connectToDevice(String deviceId) {
    final wsUrl = 'wss://api.coresync.life/ws/iot/$deviceId/';
    _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
    
    return _wsChannel!.stream.map((data) => IoTUpdate.fromJson(data));
  }
  
  // Control meditation pod
  Future<void> startMeditationSession({
    required String podId,
    required String program,
    required int duration,
  }) async {
    await _apiClient.post(
      '/api/iot/meditation-pods/$podId/start/',
      data: {
        'program': program,
        'duration': duration,
      },
    );
  }
  
  // Control AI massage bed
  Future<void> startMassageProgram({
    required String bedId,
    required String program,
    Map<String, dynamic>? customSettings,
  }) async {
    await _apiClient.post(
      '/api/iot/massage-beds/$bedId/start/',
      data: {
        'program': program,
        'settings': customSettings,
      },
    );
  }
  
  // Control immersive screens
  Future<void> setImmersiveScene({
    required String screenId,
    required String sceneId,
  }) async {
    await _apiClient.post(
      '/api/iot/screens/$screenId/scene/',
      data: {'scene': sceneId},
    );
  }
  
  // Control lighting
  Future<void> setLighting({
    required String roomId,
    required int brightness,
    String? color,
  }) async {
    await _apiClient.post(
      '/api/iot/rooms/$roomId/lighting/',
      data: {
        'brightness': brightness,
        'color': color,
      },
    );
  }
  
  // Save scene preset
  Future<void> saveScene({
    required String name,
    required Map<String, dynamic> settings,
  }) async {
    await _apiClient.post(
      '/api/iot/scenes/',
      data: {
        'name': name,
        'settings': settings,
      },
    );
  }
}
```

**Update existing page**: `lib/features/iot/presentation/pages/iot_control_page.dart`
- Implement real device control
- Add WebSocket connection
- Real-time status updates
- Error handling

---

#### 5.4 Shop & Concierge in App (Day 21)

**Shop Feature**:
```dart
// lib/features/shop/data/shop_repository.dart
class ShopRepository {
  final ApiClient _apiClient;
  
  Future<List<Product>> getProducts({String? category}) async {
    final response = await _apiClient.get(
      '/api/shop/products/',
      queryParameters: category != null ? {'category': category} : null,
    );
    return (response.data as List)
        .map((p) => Product.fromJson(p))
        .toList();
  }
  
  Future<void> addToPickupList(String productId, int quantity) async {
    await _apiClient.post(
      '/api/shop/pickup-list/',
      data: {'product': productId, 'quantity': quantity},
    );
  }
}
```

**Concierge Feature**:
```dart
// lib/features/concierge/data/concierge_repository.dart
class ConciergeRepository {
  final ApiClient _apiClient;
  
  Future<void> submitRequest({
    required String type,
    required String description,
    required double budget,
    String? productLink,
    required DateTime preferredDate,
  }) async {
    await _apiClient.post(
      '/api/concierge/',
      data: {
        'request_type': type,
        'description': description,
        'budget_range': budget,
        'product_link': productLink,
        'preferred_date': preferredDate.toIso8601String(),
      },
    );
  }
  
  Future<List<ConciergeRequest>> getMyRequests() async {
    final response = await _apiClient.get('/api/concierge/my-requests/');
    return (response.data as List)
        .map((r) => ConciergeRequest.fromJson(r))
        .toList();
  }
}
```

---

### **PRIORITY B: App Store & Play Store Preparation (Days 22-25)**

#### 6.1 iOS App Store Preparation

##### 6.1.1 Apple Developer Account Setup
1. **Реєстрація**: https://developer.apple.com/programs/
   - Вартість: $99/рік
   - Для компанії: потрібен D-U-N-S Number

2. **App Store Connect Setup**:
   - Login: https://appstoreconnect.apple.com/
   - Створити App ID: `life.coresync.app`
   - Bundle ID: `life.coresync.coresync`

##### 6.1.2 Update iOS Configuration

**File**: `coresync_mobile/ios/Runner/Info.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- App Info -->
    <key>CFBundleDisplayName</key>
    <string>CoreSync</string>
    <key>CFBundleIdentifier</key>
    <string>life.coresync.coresync</string>
    <key>CFBundleName</key>
    <string>CoreSync</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    
    <!-- Privacy Permissions -->
    <key>NSCameraUsageDescription</key>
    <string>CoreSync needs camera access for face recognition login and capturing photos.</string>
    <key>NSFaceIDUsageDescription</key>
    <string>CoreSync uses Face ID for secure and convenient authentication.</string>
    <key>NSPhotoLibraryUsageDescription</key>
    <string>CoreSync needs photo library access to upload custom content for immersive experiences.</string>
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>CoreSync uses your location to provide spa services in your area.</string>
    <key>NSBluetoothAlwaysUsageDescription</key>
    <string>CoreSync uses Bluetooth to connect with IoT devices in the spa.</string>
    
    <!-- URL Schemes for Deep Links -->
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>coresync</string>
            </array>
        </dict>
    </array>
    
    <!-- Universal Links -->
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:coresync.life</string>
        <string>applinks:www.coresync.life</string>
    </array>
</dict>
</plist>
```

##### 6.1.3 Create Apple App Site Association

**File**: `coresync_backend/static/.well-known/apple-app-site-association`
```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAM_ID.life.coresync.coresync",
        "paths": [
          "/app/*",
          "/services/*",
          "/booking/*",
          "/membership/*"
        ]
      }
    ]
  },
  "webcredentials": {
    "apps": [ "TEAM_ID.life.coresync.coresync" ]
  }
}
```

##### 6.1.4 App Store Assets

**Required Assets**:
1. **App Icon**: 1024x1024px PNG (no alpha)
   - Location: `coresync_mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset/`

2. **Screenshots** (потрібно створити):
   - iPhone 6.7" (1290x2796): 3-10 screenshots
   - iPhone 6.5" (1242x2688): 3-10 screenshots
   - iPhone 5.5" (1242x2208): optional
   - iPad Pro 12.9" (2048x2732): if supporting iPad

3. **Preview Video** (optional):
   - 15-30 seconds
   - Portrait orientation
   - MP4 format

**Screenshots List** (create these):
- Login screen with face recognition
- Home dashboard
- Service booking calendar
- IoT device control
- Membership benefits
- Concierge request form

##### 6.1.5 App Store Metadata

**App Information**:
```
Name: CoreSync
Subtitle: Premium Wellness Experience
Category: Health & Fitness
Age Rating: 4+

Description (4000 chars):
CoreSync brings the future of wellness to your fingertips. Our mobile app offers seamless access to Brooklyn's most advanced spa experience, featuring:

🤖 AI-POWERED PERSONALIZATION
• Face recognition login for instant access
• Personalized service recommendations
• Smart booking based on your preferences

🧘 ADVANCED WELLNESS TECHNOLOGY
• Control AI massage beds remotely
• Start meditation pod sessions from anywhere
• Create custom immersive screen experiences
• Adjust lighting, temperature, and scents

📅 EFFORTLESS BOOKING
• Real-time availability calendar
• One-tap booking with saved payment
• Priority access for members
• Pre-select massage programs and add-ons

💎 EXCLUSIVE MEMBER BENEFITS
• Mensuite - Men's spa access
• Coresync Private - Couple's spa experiences
• Unlimited - Full access to all amenities
• Birthday month special services

🛍️ CURATED SPA SHOP
• Premium skincare and wellness products
• Convenient pickup on your next visit
• Member-exclusive pricing

👑 PERSONAL CONCIERGE
• Special item requests
• Premium alcohol and luxury goods
• Ready for pickup on booking day

🏠 IoT SMART CONTROL
• Meditation pod programs
• Breathwork session customization
• Scene creation and sharing
• Equipment pre-configuration

CoreSync membership is required to access the app. Visit coresync.life to learn more.

Keywords:
spa, wellness, meditation, massage, facial, luxury spa, premium wellness, AI massage, biometric, face recognition, membership, brooklyn spa, mens spa, couples spa

Support URL: https://coresync.life/support
Privacy Policy URL: https://coresync.life/privacy-policy
Terms of Use URL: https://coresync.life/terms
```

##### 6.1.6 Build and Submit iOS App

**Commands**:
```bash
cd coresync_mobile

# Install dependencies
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# Build iOS
flutter build ios --release

# Open Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Select "Any iOS Device" as target
# 2. Product > Archive
# 3. Upload to App Store Connect
# 4. Submit for Review
```

**Xcode Setup**:
1. Set Team in Signing & Capabilities
2. Set Bundle Identifier: `life.coresync.coresync`
3. Set Version: 1.0.0
4. Set Build: 1
5. Add capabilities:
   - Push Notifications
   - Background Modes (Remote notifications)
   - Associated Domains

---

#### 6.2 Google Play Store Preparation

##### 6.2.1 Google Play Console Setup
1. **Реєстрація**: https://play.google.com/console/signup
   - Вартість: $25 (одноразово)

2. **Create App**:
   - App name: CoreSync
   - Default language: English (US)
   - App type: App
   - Category: Health & Fitness
   - Free/Paid: Free

##### 6.2.2 Update Android Configuration

**File**: `coresync_mobile/android/app/build.gradle`
```gradle
def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {
    throw new GradleException("Flutter SDK not found.")
}

def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    namespace "life.coresync.coresync"
    compileSdkVersion 34
    ndkVersion "25.1.8937393"

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    defaultConfig {
        applicationId "life.coresync.coresync"
        minSdkVersion 24
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
        multiDexEnabled true
    }

    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

flutter {
    source '../..'
}

dependencies {
    implementation 'androidx.multidex:multidex:2.0.1'
}
```

**File**: `coresync_mobile/android/app/src/main/AndroidManifest.xml`
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.USE_BIOMETRIC"/>
    <uses-permission android:name="android.permission.BLUETOOTH"/>
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    
    <!-- Features -->
    <uses-feature android:name="android.hardware.camera"/>
    <uses-feature android:name="android.hardware.camera.autofocus"/>
    <uses-feature android:name="android.hardware.bluetooth"/>

    <application
        android:label="CoreSync"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="false">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"/>
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
            
            <!-- Deep Links -->
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW"/>
                <category android:name="android.intent.category.DEFAULT"/>
                <category android:name="android.intent.category.BROWSABLE"/>
                <data android:scheme="https"
                      android:host="coresync.life"/>
                <data android:scheme="coresync"/>
            </intent-filter>
        </activity>
        
        <meta-data
            android:name="flutterEmbedding"
            android:value="2"/>
    </application>
</manifest>
```

##### 6.2.3 Create Digital Asset Links

**File**: `coresync_backend/static/.well-known/assetlinks.json`
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "life.coresync.coresync",
    "sha256_cert_fingerprints": [
      "REPLACE_WITH_YOUR_SHA256_FINGERPRINT"
    ]
  }
}]
```

**Get SHA256 fingerprint**:
```bash
# Generate keystore if not exists
keytool -genkey -v -keystore ~/coresync-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias coresync

# Get SHA256
keytool -list -v -keystore ~/coresync-release-key.jks -alias coresync
```

**File**: `coresync_mobile/android/key.properties`
```properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=coresync
storeFile=/Users/USERNAME/coresync-release-key.jks
```

##### 6.2.4 Play Store Assets

**Required Assets**:
1. **App Icon**: 512x512px PNG
   - High-res icon for Play Store listing

2. **Feature Graphic**: 1024x500px JPG/PNG
   - Main banner image

3. **Screenshots** (2-8 required):
   - Phone: 16:9 or 9:16, min 320px
   - 7-inch tablet: optional
   - 10-inch tablet: optional

4. **Promotional Video** (optional):
   - YouTube URL

**Create Screenshots**:
```bash
# Use Flutter screenshot tool or emulator
flutter drive --driver=test_driver/screenshot_driver.dart --target=test_driver/screenshot_app.dart
```

##### 6.2.5 Play Store Listing

**Store Listing**:
```
App name: CoreSync
Short description (80 chars):
Premium wellness experience with AI-powered personalization and IoT control

Full description (4000 chars):
[Same as iOS description]

App category: Health & Fitness
Content rating: Everyone
Contact details:
  - Email: info@coresync.life
  - Phone: +1 551-574-2281
  - Website: https://coresync.life
  
Privacy Policy: https://coresync.life/privacy-policy
```

**Categorization**:
- App: Health & Fitness
- Tags: wellness, spa, meditation, massage, luxury

##### 6.2.6 Build and Submit Android App

**Commands**:
```bash
cd coresync_mobile

# Clean and get dependencies
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# Build APK for testing
flutter build apk --release

# Build App Bundle for Play Store
flutter build appbundle --release

# Output will be at:
# build/app/outputs/bundle/release/app-release.aab
```

**Upload to Play Store**:
1. Go to Play Console: https://play.google.com/console
2. Select your app
3. Production > Create new release
4. Upload `app-release.aab`
5. Add release notes
6. Review and rollout

---

### **PRIORITY C: Firebase & Push Notifications (Day 26)**

#### 7.1 Firebase Setup

**Create Firebase Project**:
1. Go to https://console.firebase.google.com/
2. Create project: "CoreSync"
3. Add iOS app: Bundle ID `life.coresync.coresync`
4. Add Android app: Package name `life.coresync.coresync`
5. Download config files:
   - iOS: `GoogleService-Info.plist` → `ios/Runner/`
   - Android: `google-services.json` → `android/app/`

**File**: `coresync_mobile/android/build.gradle`
```gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

**File**: `coresync_mobile/android/app/build.gradle`
```gradle
// At bottom
apply plugin: 'com.google.gms.google-services'
```

#### 7.2 Push Notifications Implementation

**File**: `lib/core/services/notification_service.dart` (створити)
```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();
  
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  
  Future<void> initialize() async {
    // Request permission (iOS)
    await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    // Get FCM token
    final token = await _fcm.getToken();
    print('FCM Token: $token');
    // TODO: Send token to backend
    
    // Initialize local notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    
    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    
    // Handle background messages
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);
    
    // Handle notification opened app
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationOpen);
  }
  
  void _handleForegroundMessage(RemoteMessage message) {
    // Show local notification
    _showLocalNotification(
      title: message.notification?.title ?? '',
      body: message.notification?.body ?? '',
      payload: message.data.toString(),
    );
  }
  
  Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'coresync_channel',
      'CoreSync Notifications',
      importance: Importance.high,
      priority: Priority.high,
    );
    
    const iosDetails = DarwinNotificationDetails();
    
    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _localNotifications.show(
      DateTime.now().millisecond,
      title,
      body,
      details,
      payload: payload,
    );
  }
  
  void _handleNotificationOpen(RemoteMessage message) {
    // Navigate based on notification data
    final type = message.data['type'];
    switch (type) {
      case 'booking':
        // Navigate to booking page
        break;
      case 'service':
        // Navigate to service detail
        break;
      // ... other types
    }
  }
  
  void _onNotificationTapped(NotificationResponse response) {
    // Handle local notification tap
  }
}

// Background message handler (top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  print('Background message: ${message.messageId}');
}
```

**Update main.dart**:
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Initialize Notifications
  await NotificationService().initialize();
  
  // ... rest of initialization
}
```

---

## 🎯 PHASE 3: TESTING & OPTIMIZATION (Тиждень 5)

### **PRIORITY A: Testing (Days 27-29)**

#### 8.1 Website Testing Checklist

**Cross-browser Testing**:
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)

**Mobile Testing**:
- [ ] iOS Safari (iPhone 12, 13, 14, 15)
- [ ] Chrome Mobile (Android)
- [ ] Responsive breakpoints (320px, 375px, 768px, 1024px, 1440px)

**Page-by-Page Testing**:
- [ ] Home - hero video, navigation, animations
- [ ] Services - list, detail pages, booking integration
- [ ] Membership - pricing tables, comparison
- [ ] Shop - product grid, add to cart, pickup list
- [ ] Concierge - form submission, validation
- [ ] Dashboard - all 6 pages, API integration
- [ ] Legal - all 3 pages, formatting
- [ ] Booking Calendar - date selection, time slots

**Functionality Testing**:
- [ ] Form submissions (contacts, concierge)
- [ ] Authentication (login, signup, password reset)
- [ ] Booking flow (select service, time, confirm)
- [ ] Shop functionality (add to pickup list)
- [ ] Navigation (all links work)
- [ ] Mobile menu (open, close, smooth)

**Performance Testing**:
```bash
# Lighthouse audit
npm install -g lighthouse
lighthouse https://coresync.life --view

# Target scores:
# Performance: 90+
# Accessibility: 95+
# Best Practices: 95+
# SEO: 95+
```

#### 8.2 Mobile App Testing

**Unit Tests**: Create tests for key features
```dart
// test/features/auth/face_recognition_test.dart
void main() {
  group('FaceRecognitionUseCase', () {
    test('should register face successfully', () async {
      // Test implementation
    });
    
    test('should authenticate face successfully', () async {
      // Test implementation
    });
  });
}
```

**Widget Tests**:
```dart
// test/features/booking/booking_page_test.dart
void main() {
  testWidgets('BookingPage shows calendar', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: BookingPage()));
    expect(find.byType(CalendarWidget), findsOneWidget);
  });
}
```

**Integration Tests**:
```dart
// integration_test/app_test.dart
void main() {
  testWidgets('Full booking flow', (tester) async {
    // 1. Open app
    // 2. Login with face
    // 3. Navigate to booking
    // 4. Select service
    // 5. Confirm booking
    // 6. Verify success
  });
}
```

**Device Testing**:
- [ ] iOS: iPhone 12 Pro, iPhone 14, iPad Pro
- [ ] Android: Pixel 6, Samsung Galaxy S22, OnePlus 9

**Feature Testing**:
- [ ] Face recognition (registration + login)
- [ ] Booking flow (end-to-end)
- [ ] IoT controls (all devices)
- [ ] Shop (browse, add to pickup)
- [ ] Concierge (submit request)
- [ ] Push notifications (receive, tap)
- [ ] Deep links (open from web)

#### 8.3 API Testing

**Create API tests**:
```python
# coresync_backend/tests/test_api.py
from django.test import TestCase
from rest_framework.test import APIClient

class BookingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user and authenticate
    
    def test_get_available_slots(self):
        response = self.client.get('/api/bookings/available-slots/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_booking(self):
        data = {
            'service': 'service-id',
            'datetime': '2025-10-15T10:00:00Z',
        }
        response = self.client.post('/api/bookings/', data)
        self.assertEqual(response.status_code, 201)
```

**Run tests**:
```bash
cd coresync_backend
python manage.py test

# Coverage report
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

### **PRIORITY B: Performance Optimization (Days 30-31)**

#### 9.1 Website Optimization

**Image Optimization**:
```bash
# Install tools
npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg

# Optimize images
cd coresync_backend/static/images
for file in *.jpg; do
    imagemin "$file" --plugin=mozjpeg --plugin=webp > "${file%.*}.webp"
done
```

**CSS Optimization**:
```bash
# Minify CSS
npm install -g clean-css-cli
cleancss -o styles.min.css styles.css
```

**JavaScript Optimization**:
```bash
# Minify JS
npm install -g terser
terser booking.js -o booking.min.js --compress --mangle
```

**Django Settings** for production:
```python
# settings.py

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# Static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
```

#### 9.2 Mobile App Optimization

**Build Size Optimization**:
```bash
# Analyze app size
flutter build apk --analyze-size
flutter build appbundle --analyze-size

# Split APKs by ABI
flutter build apk --split-per-abi
```

**Performance Profiling**:
```bash
# Profile performance
flutter run --profile
# Then use DevTools: flutter pub global run devtools
```

**Optimization checklist**:
- [ ] Remove unused packages
- [ ] Use `const` widgets where possible
- [ ] Lazy load images with `cached_network_image`
- [ ] Implement pagination for lists
- [ ] Cache API responses
- [ ] Optimize animations (use `AnimatedBuilder`)

---

## 🎯 PHASE 4: DEPLOYMENT & LAUNCH (Тиждень 6)

### **PRIORITY A: Production Deployment (Days 32-35)**

#### 10.1 Backend Deployment to Render.com

**Environment Variables** (в Render dashboard):
```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=coresync.life,www.coresync.life,api.coresync.life

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# QuickBooks
QUICKBOOKS_CLIENT_ID=...
QUICKBOOKS_CLIENT_SECRET=...
QUICKBOOKS_REDIRECT_URI=https://api.coresync.life/quickbooks/callback

# Firebase
FIREBASE_ADMIN_SDK=<JSON content>

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=info@coresync.life
EMAIL_HOST_PASSWORD=...

# AWS S3 (for media files)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=coresync-media
AWS_S3_REGION_NAME=us-east-1

# Google Analytics
GA_MEASUREMENT_ID=G-...

# Sentry
SENTRY_DSN=https://...@sentry.io/...
```

**Render Blueprint** (вже є `render.yaml`):
```yaml
services:
  - type: web
    name: coresync-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.0
      - key: DATABASE_URL
        fromDatabase:
          name: coresync-db
          property: connectionString
    healthCheckPath: /health/
```

**Deploy**:
```bash
# Connect to Render
git remote add render <render-git-url>

# Deploy
git push render main

# Check logs
render logs -t coresync-backend
```

#### 10.2 Domain Setup (GoDaddy)

**DNS Configuration**:
```
Type    Name          Value                          TTL
A       @             76.76.21.21 (Render IP)       1 Hour
A       www           76.76.21.21                   1 Hour
CNAME   api           coresync-backend.onrender.com 1 Hour
TXT     @             v=spf1 include:_spf.google.com ~all
```

**SSL Certificate**: Render provides automatic SSL (Let's Encrypt)

**Django Settings**:
```python
# settings.py
ALLOWED_HOSTS = ['coresync.life', 'www.coresync.life', 'api.coresync.life']

# Force HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 10.3 SEO Configuration

**File**: `coresync_backend/templates/base.html` (update head)
```html
<head>
    <!-- Basic Meta -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    
    <!-- SEO Meta -->
    <title>{% block title %}CoreSync - Premium Wellness Experience{% endblock %}</title>
    <meta name="description" content="{% block description %}Brooklyn's most advanced spa featuring AI-powered massage beds, meditation pods, and immersive wellness experiences.{% endblock %}">
    <meta name="keywords" content="luxury spa brooklyn, wellness center, AI massage, meditation pod, couples spa, mens spa, premium wellness">
    <meta name="author" content="CoreSync">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}CoreSync - Premium Wellness Experience{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Brooklyn's most advanced spa featuring AI-powered technology.{% endblock %}">
    <meta property="og:image" content="{% block og_image %}https://coresync.life/static/images/og-image.jpg{% endblock %}">
    <meta property="og:url" content="{% block og_url %}https://coresync.life{% endblock %}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="CoreSync">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{% block twitter_title %}CoreSync - Premium Wellness Experience{% endblock %}">
    <meta name="twitter:description" content="{% block twitter_description %}Brooklyn's most advanced spa.{% endblock %}">
    <meta name="twitter:image" content="{% block twitter_image %}https://coresync.life/static/images/twitter-card.jpg{% endblock %}">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{% block canonical %}https://coresync.life{% endblock %}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="{% static 'favicon.png' %}">
    <link rel="apple-touch-icon" sizes="180x180" href="{% static 'apple-touch-icon.png' %}">
    
    <!-- Google Analytics 4 -->
    {% if GA_MEASUREMENT_ID %}
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_MEASUREMENT_ID }}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '{{ GA_MEASUREMENT_ID }}');
    </script>
    {% endif %}
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": "CoreSync",
        "description": "Premium wellness spa in Brooklyn featuring AI-powered technology",
        "url": "https://coresync.life",
        "logo": "https://coresync.life/static/images/logo.png",
        "image": "https://coresync.life/static/images/og-image.jpg",
        "telephone": "+15515742281",
        "email": "info@coresync.life",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "1544 71st Street",
            "addressLocality": "Brooklyn",
            "addressRegion": "NY",
            "postalCode": "11228",
            "addressCountry": "US"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "40.6234",
            "longitude": "-74.0068"
        },
        "openingHours": "Mo-Su 09:00-22:00",
        "priceRange": "$$$",
        "sameAs": [
            "https://www.instagram.com/coresync",
            "https://www.facebook.com/coresync"
        ]
    }
    </script>
</head>
```

**Create sitemap.xml**:
```xml
<!-- coresync_backend/templates/sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://coresync.life/</loc>
        <lastmod>2025-10-08</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://coresync.life/services/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://coresync.life/membership/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <!-- ... more URLs -->
</urlset>
```

**robots.txt**:
```txt
# coresync_backend/static/robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dashboard/
Disallow: /api/

Sitemap: https://coresync.life/sitemap.xml
```

#### 10.4 Monitoring & Logging

**Sentry Integration**:
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment='production',
)
```

**Logging Configuration**:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

### **PRIORITY B: App Store & Play Store Submission (Days 36-38)**

#### 11.1 Final Pre-submission Checklist

**iOS App Store**:
- [ ] App icon (1024x1024)
- [ ] Screenshots (all sizes)
- [ ] Privacy policy URL
- [ ] Terms of use URL
- [ ] App description and keywords
- [ ] Support URL and email
- [ ] Content rating completed
- [ ] Pricing and availability set
- [ ] Build uploaded and processed
- [ ] TestFlight testing completed
- [ ] App review information filled
- [ ] Demo account credentials (if required)

**Google Play Store**:
- [ ] App icon (512x512)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (phone + tablet)
- [ ] Privacy policy URL
- [ ] App description
- [ ] Content rating questionnaire
- [ ] Pricing and distribution
- [ ] Store listing complete
- [ ] App bundle uploaded
- [ ] Internal testing track completed
- [ ] Production release ready

#### 11.2 App Review Preparation

**Demo Account** (для reviewers):
```
Email: demo@coresync.life
Password: ReviewDemo2025!

Membership: Premium (pre-configured)
Face Recognition: Disabled for demo account
Payment Method: Test card pre-saved
```

**Review Notes** (для App Store):
```
Thank you for reviewing CoreSync!

IMPORTANT NOTES:
1. Face Recognition: You can skip face registration by using the demo account provided.
2. Membership Required: The demo account has an active Premium membership.
3. IoT Features: Some IoT controls require physical devices at our spa location. Demo mode is available for testing.
4. Payment: Test Stripe credentials are configured for testing bookings.

TESTING GUIDE:
1. Login with demo credentials
2. Explore home dashboard
3. Browse services catalog
4. Create a test booking
5. View IoT control panel (demo mode)
6. Browse shop and add items to pickup list
7. Submit a concierge request

Contact: info@coresync.life for any questions.
```

#### 11.3 Submit Apps

**iOS Submission**:
```bash
# Final build
cd coresync_mobile
flutter clean
flutter pub get
flutter build ios --release

# Open Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Archive (Product > Archive)
# 2. Distribute App > App Store Connect
# 3. Upload
# 4. Go to App Store Connect
# 5. Fill all metadata
# 6. Submit for Review
```

**Android Submission**:
```bash
# Final build
cd coresync_mobile
flutter clean
flutter pub get
flutter build appbundle --release

# Upload to Play Console
# 1. Go to https://play.google.com/console
# 2. Select app
# 3. Production > Create new release
# 4. Upload app-release.aab
# 5. Fill release notes
# 6. Review and roll out to production
```

**Expected Review Times**:
- iOS: 24-48 hours
- Android: 1-7 days

---

## 🎯 PHASE 5: FINAL TOUCHES (Тиждень 7)

### **PRIORITY A: Documentation (Days 39-40)**

#### 12.1 API Documentation

**Install Swagger**:
```bash
pip install drf-spectacular
```

**Configure**:
```python
# settings.py
INSTALLED_APPS += ['drf_spectacular']

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'CoreSync API',
    'DESCRIPTION': 'Premium wellness spa API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

**URLs**:
```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

#### 12.2 User Documentation

**Create**: `coresync_backend/templates/docs/` pages
- Getting Started Guide
- Booking Guide
- Membership Benefits Guide
- App User Manual
- FAQ

#### 12.3 Admin Manual

**Create**: `docs/ADMIN_MANUAL.md`
- Django admin guide
- Managing members
- Handling bookings
- Processing concierge requests
- Managing inventory
- Financial reports
- System maintenance

---

### **PRIORITY B: Training & Handoff (Days 41-42)**

#### 13.1 Staff Training Materials

**Create training videos** (or documents):
1. Admin Dashboard Overview
2. Managing Member Accounts
3. Booking Management
4. Concierge Request Processing
5. Shop Inventory Management
6. IoT Device Control (when available)
7. Financial Reporting
8. Customer Support Procedures

#### 13.2 Technical Handoff

**Deliverables**:
- [ ] Complete source code (GitHub access)
- [ ] Environment variables documentation
- [ ] API documentation (Swagger)
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Admin manual
- [ ] App Store/Play Store credentials
- [ ] Firebase console access
- [ ] Stripe dashboard access
- [ ] Render.com dashboard access
- [ ] Domain management access (GoDaddy)

**Handoff Meeting Agenda**:
1. Project overview and achievements
2. Architecture walkthrough
3. Admin panel demonstration
4. Mobile app demonstration
5. Deployment process
6. Monitoring and maintenance
7. Future enhancements roadmap
8. Q&A and knowledge transfer

---

## 📋 SUMMARY CHECKLIST

### Website (23 pages total)
- [x] Home (готово)
- [x] Private (готово)
- [x] Menssuite (готово)
- [x] Services List (готово)
- [ ] Service Detail (покращити)
- [x] Membership (готово)
- [x] Contacts (готово)
- [x] About (готово)
- [x] Technologies (готово, розширити)
- [x] Booking Calendar (готово)
- [x] Dashboard (6 pages) (готово)
- [x] Auth (3 pages) (готово)
- [ ] Shop (створити)
- [ ] Concierge (створити)
- [ ] Privacy Policy (створити)
- [ ] Terms of Service (створити)
- [ ] Refund Policy (створити)

### Backend API
- [x] Authentication
- [x] Users
- [x] Services
- [x] Memberships
- [x] Bookings (активувати)
- [ ] Shop (створити)
- [ ] Concierge (створити)
- [x] Payments (активувати)
- [x] IoT Control (готово до налаштування)

### Mobile App
- [ ] Face Recognition (реалізувати)
- [ ] Real-time Booking (реалізувати)
- [ ] IoT Control (реалізувати)
- [ ] Shop (реалізувати)
- [ ] Concierge (реалізувати)
- [ ] Push Notifications (реалізувати)
- [ ] App Store Submission (підготувати)
- [ ] Play Store Submission (підготувати)

### Deployment
- [ ] Production Backend (Render.com)
- [ ] Domain Setup (GoDaddy)
- [ ] SSL Certificates (автоматично)
- [ ] SEO Configuration
- [ ] GA4 Integration
- [ ] Monitoring (Sentry)

### Final
- [ ] Testing (all platforms)
- [ ] Performance Optimization
- [ ] Documentation
- [ ] Staff Training
- [ ] App Store Launch
- [ ] Play Store Launch

---

## 🎯 ESTIMATED TIMELINE

**Weeks 1-2**: Website Completion (10 pages + optimization)
**Weeks 3-4**: Mobile App Completion (all features + store prep)
**Week 5**: Testing & Optimization
**Week 6**: Deployment & Launch
**Week 7**: Documentation & Training

**Total**: 7 weeks to 99% completion

**Після 99%**:
- Отримання відео контенту (від клієнта)
- Фінальне IoT налаштування (від постачальників)
- App Store/Play Store approval (1-2 тижні)
- **LAUNCH! 🚀**

---

## 💰 RESOURCES NEEDED

### От клієнта:
1. **Відео контент** (3-5 videos)
2. **Професійні фото** (products, team, facility)
3. **IoT обладнання API документація**
4. **Apple Developer account** ($99/year)
5. **Google Play Developer account** ($25 one-time)
6. **Domain access** (GoDaddy credentials)
7. **GA4 Measurement ID**
8. **Content for legal pages** (privacy, terms, refund)

### Технічні:
1. **Render.com** (hosting) - ~$25-50/month
2. **PostgreSQL database** (Render included)
3. **Redis** (Render) - optional
4. **AWS S3** (media storage) - ~$5-10/month
5. **Firebase** (notifications) - Free tier
6. **Sentry** (monitoring) - Free tier
7. **Stripe** (payments) - per transaction fees

---

## 🚀 READY TO START!

Цей план забезпечує:
✅ Повну готовність сайту (100%)
✅ Повну готовність мобільного додатку (100%)
✅ Production deployment
✅ App Store + Play Store submission
✅ Відсутність технічних боргів
✅ Чистий, maintainable код
✅ Comprehensive documentation

**Залишиться тільки**:
1. Отримати відео від клієнта
2. Налаштувати IoT пристрої (коли будуть)
3. Дочекатися App Store/Play Store approval

**Проект буде готовий до повного запуску! 🎉**

