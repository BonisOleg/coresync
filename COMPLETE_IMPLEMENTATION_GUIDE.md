# 🎯 CORESYNC - COMPLETE 42-DAY IMPLEMENTATION GUIDE

**Version**: FINAL 1.0  
**Total Duration**: 42 days (6 weeks)  
**Target**: 99% completion  
**Quality Level**: Production-Ready

---

## 📅 WEEK 1: BACKEND + SHOP/CONCIERGE (Days 1-7)

### ✅ **Day 1**: Shop Backend (models, serializers, views, admin)
### ✅ **Day 2**: Shop Frontend (HTML, CSS, JavaScript with DashboardAPI)
### ✅ **Day 3**: Concierge Backend (models, serializers, views, admin)
### ✅ **Day 4**: Concierge Frontend (HTML, CSS, JavaScript)
### ✅ **Day 5**: Migrations + Admin Testing + Initial Data
### ✅ **Day 6**: Privacy Policy + Legal page structure
### ✅ **Day 7**: Terms of Service + Refund Policy

**See ULTIMATE_DEVELOPMENT_PLAN.md for detailed code (Days 1-10)**

---

## 📅 WEEK 2: WEBSITE ENHANCEMENTS (Days 8-14)

### **Day 11: Enhanced Service Detail Page**

**Update**: `templates/services/detail.html`

**Add sections**:
1. **Image Gallery** (use carousel-shared.js)
2. **Pricing Tiers** (member vs non-member)
3. **Available Add-ons** with checkboxes
4. **Quick Book** button with date picker
5. **Reviews section** (placeholder for future)

**File**: `static/js/service-detail.js` (new)
```javascript
class ServiceDetail extends DashboardAPI {
    constructor(serviceSlug) {
        super();
        this.serviceSlug = serviceSlug;
        this.selectedAddons = [];
        this.init();
    }
    
    async init() {
        await this.loadServiceDetails();
        this.setupBookingButton();
        this.setupAddonSelection();
    }
    
    async loadServiceDetails() {
        try {
            const service = await this.request(`/services/${this.serviceSlug}/`);
            this.service = service;
            this.renderPricing(service);
            this.loadAddons();
        } catch (error) {
            console.error('Error loading service:', error);
        }
    }
    
    async loadAddons() {
        try {
            const addons = await this.request(`/services/${this.serviceSlug}/addons/`);
            this.renderAddons(addons);
        } catch (error) {
            console.error('Error loading addons:', error);
        }
    }
    
    renderPricing(service) {
        const container = document.getElementById('pricing-tiers');
        if (!container) return;
        
        container.innerHTML = `
            <div class="pricing-grid">
                <div class="pricing-card">
                    <h3>Non-Member</h3>
                    <div class="price">$${service.non_member_price}</div>
                </div>
                <div class="pricing-card featured">
                    <h3>Member Price</h3>
                    <div class="price">$${service.member_price}</div>
                    <div class="savings">Save $${(service.non_member_price - service.member_price).toFixed(2)}</div>
                </div>
                ${service.category === 'unlimited' ? `
                    <div class="pricing-card premium">
                        <h3>Unlimited Members</h3>
                        <div class="price">Included</div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    renderAddons(addons) {
        const container = document.getElementById('service-addons');
        if (!container || addons.length === 0) return;
        
        container.innerHTML = `
            <h3>Available Add-ons</h3>
            <div class="addons-list">
                ${addons.map(addon => `
                    <label class="addon-checkbox">
                        <input 
                            type="checkbox" 
                            value="${addon.id}"
                            data-price="${addon.price}"
                            onchange="serviceDetail.toggleAddon(${addon.id}, ${addon.price})"
                        >
                        <span>${addon.name} - $${addon.price}</span>
                    </label>
                `).join('')}
            </div>
            <div class="addon-total" style="margin-top: 1rem; font-weight: bold;">
                Add-ons Total: $<span id="addons-total">0.00</span>
            </div>
        `;
    }
    
    toggleAddon(addonId, price) {
        const checkbox = document.querySelector(`input[value="${addonId}"]`);
        
        if (checkbox.checked) {
            this.selectedAddons.push({ id: addonId, price });
        } else {
            this.selectedAddons = this.selectedAddons.filter(a => a.id !== addonId);
        }
        
        this.updateAddonsTotal();
    }
    
    updateAddonsTotal() {
        const total = this.selectedAddons.reduce((sum, addon) => sum + addon.price, 0);
        const totalElement = document.getElementById('addons-total');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2);
        }
    }
    
    setupBookingButton() {
        const bookBtn = document.getElementById('quick-book-btn');
        if (bookBtn) {
            bookBtn.addEventListener('click', () => {
                // Redirect to booking page with pre-selected service
                window.location.href = `/book/?service=${this.serviceSlug}&addons=${this.selectedAddons.map(a => a.id).join(',')}`;
            });
        }
    }
}
```

---

### **Day 12: Dashboard Membership Detail Enhancement**

**Update**: `templates/dashboard/membership.html`

**Add sections**:
```html
<!-- Usage Analytics -->
<section class="membership-stats">
    <h2>Your Usage This Month</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="services-used">0</div>
            <div class="stat-label">Services Used</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="total-savings">$0</div>
            <div class="stat-label">Total Savings</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="visit-count">0</div>
            <div class="stat-label">Spa Visits</div>
        </div>
    </div>
</section>

<!-- Benefits -->
<section class="membership-benefits">
    <h2>Your Benefits</h2>
    <div id="benefits-list"></div>
</section>

<!-- Upgrade Path -->
<section class="membership-upgrade">
    <h2>Upgrade Your Experience</h2>
    <div id="upgrade-options"></div>
</section>
```

**JavaScript**: Update `dashboard.js` or create `membership-detail.js`

---

### **Day 13: About Us Page Enhancement**

**Update**: `templates/pages/about.html`

**Add sections**:
- Founder's story with photo
- Team members grid
- Timeline of milestones
- Community commitment

---

### **Day 14: Technologies Page Enhancement**

**Update**: `templates/pages/technologies.html`

**Add detailed sections for each device**:
- AI Massage Bed specifications
- Meditation Pods features
- Oxygen Dome benefits
- Immersive Screens technology
- Smart Mirror capabilities

**Add tabs for navigation between devices**

---

## 📅 WEEK 3: FLUTTER CORE FEATURES (Days 15-21)

### **Days 15-16: Face Recognition (COMPLETE)**

**Already included in ULTIMATE_DEVELOPMENT_PLAN.md**

**Additional files needed**:

#### **File**: `lib/features/auth/presentation/pages/face_registration_page.dart`
```dart
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/repositories/face_recognition_repository.dart';

class FaceRegistrationPage extends ConsumerStatefulWidget {
  const FaceRegistrationPage({super.key});
  
  @override
  ConsumerState<FaceRegistrationPage> createState() => _FaceRegistrationPageState();
}

class _FaceRegistrationPageState extends ConsumerState<FaceRegistrationPage> {
  CameraController? _cameraController;
  final FaceRecognitionRepository _faceRepo = FaceRecognitionRepository();
  bool _isProcessing = false;
  String _statusMessage = 'Position your face in the circle';
  int _captureCount = 0;
  final int _requiredCaptures = 3; // Multiple angles for better accuracy
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      final frontCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );
      
      _cameraController = CameraController(
        frontCamera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );
      
      await _cameraController!.initialize();
      
      if (mounted) {
        setState(() {});
        _startCapture();
      }
    } catch (e) {
      print('Camera initialization error: $e');
      if (mounted) {
        setState(() => _statusMessage = 'Camera error. Please try again.');
      }
    }
  }
  
  void _startCapture() {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }
    
    _cameraController!.startImageStream(_processCameraImage);
  }
  
  void _processCameraImage(CameraImage image) async {
    if (_isProcessing || _captureCount >= _requiredCaptures) {
      return;
    }
    
    setState(() => _isProcessing = true);
    
    try {
      final success = await _faceRepo.registerFace(image);
      
      if (success) {
        _captureCount++;
        
        if (_captureCount >= _requiredCaptures) {
          setState(() => _statusMessage = 'Face registered successfully!');
          await _cameraController!.stopImageStream();
          
          await Future.delayed(const Duration(seconds: 1));
          
          if (mounted) {
            Navigator.of(context).pop(true);
          }
        } else {
          setState(() {
            _statusMessage = 'Capture ${_captureCount}/$_requiredCaptures complete. Turn slightly...';
          });
        }
      } else {
        setState(() => _statusMessage = 'Face not detected clearly. Try again.');
      }
    } catch (e) {
      setState(() => _statusMessage = 'Error processing face. Try again.');
    } finally {
      if (_captureCount < _requiredCaptures) {
        await Future.delayed(const Duration(milliseconds: 500));
        setState(() => _isProcessing = false);
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(color: Color(0xFFB8860B)),
              const SizedBox(height: 20),
              Text(
                'Initializing camera...',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          ),
        ),
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
          // Camera preview (full screen)
          Positioned.fill(
            child: CameraPreview(_cameraController!),
          ),
          
          // Dark overlay with cutout for face
          Positioned.fill(
            child: CustomPaint(
              painter: FaceOverlayPainter(),
            ),
          ),
          
          // Progress indicator
          Positioned(
            top: 100,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Text(
                  '$_captureCount / $_requiredCaptures captures',
                  style: const TextStyle(
                    color: Color(0xFFB8860B),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
          
          // Status message
          Positioned(
            bottom: 120,
            left: 20,
            right: 20,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.8),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _statusMessage,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
          
          // Instructions
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Text(
              'Keep your face within the circle\nLook directly at the camera',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 14,
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
    _faceRepo.dispose();
    super.dispose();
  }
}

/// Custom painter for face oval overlay
class FaceOverlayPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.6)
      ..style = PaintingStyle.fill;
    
    // Draw dark overlay
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);
    
    // Cut out oval for face
    final ovalRect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2.5),
      width: size.width * 0.7,
      height: size.width * 0.9,
    );
    
    paint.blendMode = BlendMode.clear;
    canvas.drawOval(ovalRect, paint);
    
    // Draw oval border
    final borderPaint = Paint()
      ..color = const Color(0xFFB8860B)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    
    canvas.drawOval(ovalRect, borderPaint);
  }
  
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
```

---

### **Days 17-18: Flutter Booking Implementation**

**File**: `lib/features/booking/data/repositories/booking_repository.dart`
```dart
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../models/booking_model.dart';
import '../models/time_slot_model.dart';

class BookingRepository {
  final ApiClient _apiClient;
  
  BookingRepository(this._apiClient);
  
  /// Get available time slots for a date
  Future<List<TimeSlot>> getAvailableSlots({
    required DateTime date,
    String? serviceId,
    String? roomType,
  }) async {
    try {
      final queryParams = {
        'date': date.toIso8601String().split('T')[0],
        if (serviceId != null) 'service_id': serviceId,
        if (roomType != null) 'room_type': roomType,
      };
      
      final response = await _apiClient.get(
        '/bookings/availability/',
        queryParameters: queryParams,
      );
      
      final List slots = response['available_slots'] ?? [];
      return slots.map((slot) => TimeSlot.fromJson(slot)).toList();
    } catch (e) {
      throw Exception('Failed to load availability: $e');
    }
  }
  
  /// Create new booking
  Future<Booking> createBooking({
    required String serviceId,
    required DateTime date,
    required String startTime,
    required String roomId,
    List<int> addonIds = const [],
    String? specialRequests,
    String? aiProgram,
    Map<String, dynamic>? scenePreferences,
  }) async {
    try {
      final data = {
        'service_id': serviceId,
        'date': date.toIso8601String().split('T')[0],
        'start_time': startTime,
        'room_id': roomId,
        if (addonIds.isNotEmpty) 'addons': addonIds.map((id) => {'id': id}).toList(),
        if (specialRequests != null) 'special_requests': specialRequests,
        if (aiProgram != null) 'ai_program': aiProgram,
        if (scenePreferences != null) 'scene_preferences': scenePreferences,
      };
      
      final response = await _apiClient.post(
        '/bookings/create_booking/',
        data: data,
      );
      
      return Booking.fromJson(response);
    } catch (e) {
      throw Exception('Failed to create booking: $e');
    }
  }
  
  /// Get user's bookings
  Future<Map<String, List<Booking>>> getMyBookings() async {
    try {
      final response = await _apiClient.get('/bookings/my_bookings/');
      
      final List upcoming = response['upcoming'] ?? [];
      final List past = response['past'] ?? [];
      
      return {
        'upcoming': upcoming.map((b) => Booking.fromJson(b)).toList(),
        'past': past.map((b) => Booking.fromJson(b)).toList(),
      };
    } catch (e) {
      throw Exception('Failed to load bookings: $e');
    }
  }
  
  /// Cancel booking
  Future<void> cancelBooking(int bookingId, {String? reason}) async {
    try {
      await _apiClient.post(
        '/bookings/$bookingId/cancel_booking/',
        data: {'reason': reason ?? 'Cancelled by customer'},
      );
    } catch (e) {
      throw Exception('Failed to cancel booking: $e');
    }
  }
}
```

**File**: `lib/features/booking/data/models/booking_model.dart`
```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'booking_model.freezed.dart';
part 'booking_model.g.dart';

@freezed
class Booking with _$Booking {
  const factory Booking({
    required int id,
    required String bookingReference,
    required String serviceName,
    required String serviceCategory,
    required String date,
    required String startTime,
    required String endTime,
    required String roomName,
    required String status,
    required bool canCancel,
    required bool canReschedule,
    required String finalTotal,
    required String paymentStatus,
  }) = _Booking;
  
  factory Booking.fromJson(Map<String, dynamic> json) => _$BookingFromJson(json);
}

@freezed
class TimeSlot with _$TimeSlot {
  const factory TimeSlot({
    required int id,
    required String startTime,
    required String endTime,
    required int roomId,
    required String roomName,
    required String roomType,
    required int availableSpots,
    required bool isPremiumSlot,
    required bool hasIotControl,
    String? price,
    Map<String, dynamic>? priorityInfo,
  }) = _TimeSlot;
  
  factory TimeSlot.fromJson(Map<String, dynamic> json) => _$TimeSlotFromJson(json);
}
```

**File**: `lib/features/booking/presentation/pages/booking_page.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../data/repositories/booking_repository.dart';
import '../../../../core/di/service_locator.dart';

class BookingPage extends ConsumerStatefulWidget {
  const BookingPage({super.key});
  
  @override
  ConsumerState<BookingPage> createState() => _BookingPageState();
}

class _BookingPageState extends ConsumerState<BookingPage> {
  late final BookingRepository _bookingRepo;
  DateTime _selectedDate = DateTime.now();
  DateTime _focusedDate = DateTime.now();
  List<TimeSlot> _availableSlots = [];
  TimeSlot? _selectedSlot;
  bool _isLoading = false;
  
  @override
  void initState() {
    super.initState();
    _bookingRepo = getIt<BookingRepository>();
    _loadAvailability();
  }
  
  Future<void> _loadAvailability() async {
    setState(() => _isLoading = true);
    
    try {
      final slots = await _bookingRepo.getAvailableSlots(
        date: _selectedDate,
      );
      
      setState(() {
        _availableSlots = slots;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Failed to load availability');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Book a Service'),
      ),
      body: Column(
        children: [
          // Calendar
          TableCalendar(
            firstDay: DateTime.now(),
            lastDay: DateTime.now().add(const Duration(days: 90)),
            focusedDay: _focusedDate,
            selectedDayPredicate: (day) => isSameDay(_selectedDate, day),
            onDaySelected: (selectedDay, focusedDay) {
              setState(() {
                _selectedDate = selectedDay;
                _focusedDate = focusedDay;
                _selectedSlot = null;
              });
              _loadAvailability();
            },
            calendarStyle: CalendarStyle(
              selectedDecoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
                shape: BoxShape.circle,
              ),
              todayDecoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                shape: BoxShape.circle,
              ),
            ),
          ),
          
          const Divider(),
          
          // Time slots
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _availableSlots.isEmpty
                    ? const Center(child: Text('No available slots'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _availableSlots.length,
                        itemBuilder: (context, index) {
                          final slot = _availableSlots[index];
                          final isSelected = _selectedSlot == slot;
                          
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              selected: isSelected,
                              title: Text('${slot.startTime} - ${slot.endTime}'),
                              subtitle: Text('${slot.roomName} • ${slot.availableSpots} spots'),
                              trailing: slot.price != null
                                  ? Text(
                                      '\$${slot.price}',
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  : null,
                              onTap: () {
                                setState(() => _selectedSlot = slot);
                              },
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
      bottomNavigationBar: _selectedSlot != null
          ? SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: ElevatedButton(
                  onPressed: _confirmBooking,
                  child: const Text('Confirm Booking'),
                ),
              ),
            )
          : null,
    );
  }
  
  Future<void> _confirmBooking() async {
    if (_selectedSlot == null) return;
    
    // Navigate to booking confirmation page
    // or show booking dialog with add-ons selection
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
  
  @override
  void dispose() {
    _cameraController?.dispose();
    _faceRepo.dispose();
    super.dispose();
  }
}
```

**Add package**: `table_calendar: ^3.0.9` to `pubspec.yaml`

---

### **Days 19-20: Flutter IoT Control**

**File**: `lib/features/iot/data/repositories/iot_repository.dart`
```dart
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import '../../../../core/network/api_client.dart';
import '../models/iot_device_model.dart';
import '../models/scene_model.dart';

class IoTRepository {
  final ApiClient _apiClient;
  WebSocketChannel? _wsChannel;
  
  IoTRepository(this._apiClient);
  
  /// Connect to WebSocket for real-time device updates
  Stream<Map<String, dynamic>> connectToDeviceUpdates() {
    final wsUrl = 'wss://api.coresync.life/ws/iot/updates/';
    _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
    
    return _wsChannel!.stream.map((data) {
      return jsonDecode(data) as Map<String, dynamic>;
    });
  }
  
  /// Get available IoT devices
  Future<List<IoTDevice>> getDevices({String? location}) async {
    try {
      final response = await _apiClient.get(
        '/iot/devices/',
        queryParameters: location != null ? {'location': location} : null,
      );
      
      final List devices = response['devices'] ?? response;
      return devices.map((d) => IoTDevice.fromJson(d)).toList();
    } catch (e) {
      throw Exception('Failed to load devices: $e');
    }
  }
  
  /// Control lighting
  Future<void> setLighting({
    required String roomId,
    required int brightness,
    String? color,
  }) async {
    await _apiClient.post(
      '/iot/lighting/control/',
      data: {
        'room': roomId,
        'brightness': brightness,
        if (color != null) 'color': color,
      },
    );
  }
  
  /// Control temperature
  Future<void> setTemperature({
    required String roomId,
    required double temperature,
  }) async {
    await _apiClient.post(
      '/iot/temperature/control/',
      data: {
        'room': roomId,
        'temperature': temperature,
      },
    );
  }
  
  /// Start meditation session
  Future<void> startMeditation({
    required String podId,
    required String program,
    required int duration,
  }) async {
    await _apiClient.post(
      '/iot/meditation/start/',
      data: {
        'pod_id': podId,
        'program': program,
        'duration': duration,
      },
    );
  }
  
  /// Start massage program
  Future<void> startMassage({
    required String bedId,
    required String program,
    Map<String, dynamic>? settings,
  }) async {
    await _apiClient.post(
      '/iot/massage/start/',
      data: {
        'bed_id': bedId,
        'program': program,
        if (settings != null) 'settings': settings,
      },
    );
  }
  
  /// Set immersive scene
  Future<void> setScene({
    required String screenId,
    required String sceneId,
  }) async {
    await _apiClient.post(
      '/iot/screens/scene/',
      data: {
        'screen_id': screenId,
        'scene_id': sceneId,
      },
    );
  }
  
  /// Get user's saved scenes
  Future<List<Scene>> getMySce nes() async {
    final response = await _apiClient.get('/iot/scenes/my-scenes/');
    final List scenes = response['scenes'] ?? response;
    return scenes.map((s) => Scene.fromJson(s)).toList();
  }
  
  /// Create custom scene
  Future<Scene> createScene({
    required String name,
    required String description,
    required Map<String, dynamic> deviceSettings,
    String? location,
  }) async {
    final response = await _apiClient.post(
      '/iot/scenes/',
      data: {
        'name': name,
        'description': description,
        'device_settings': deviceSettings,
        if (location != null) 'location': location,
      },
    );
    
    return Scene.fromJson(response);
  }
  
  /// Activate scene
  Future<void> activateScene(int sceneId) async {
    await _apiClient.post('/iot/scenes/$sceneId/activate/');
  }
  
  void dispose() {
    _wsChannel?.sink.close();
  }
}
```

**File**: `lib/features/iot/presentation/pages/iot_control_page.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/repositories/iot_repository.dart';
import '../../../../core/di/service_locator.dart';

class IoTControlPage extends ConsumerStatefulWidget {
  const IoTControlPage({super.key});
  
  @override
  ConsumerState<IoTControlPage> createState() => _IoTControlPageState();
}

class _IoTControlPageState extends ConsumerState<IoTControlPage> {
  late final IoTRepository _iotRepo;
  int _selectedTab = 0;
  
  // Control states
  double _lightingBrightness = 50;
  double _temperature = 72;
  String? _selectedScene;
  
  @override
  void initState() {
    super.initState();
    _iotRepo = getIt<IoTRepository>();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('IoT Control'),
      ),
      body: Column(
        children: [
          // Tab bar
          Container(
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Theme.of(context).dividerColor,
                ),
              ),
            ),
            child: Row(
              children: [
                _buildTab('Lighting', 0),
                _buildTab('Climate', 1),
                _buildTab('Scenes', 2),
                _buildTab('Devices', 3),
              ],
            ),
          ),
          
          // Tab content
          Expanded(
            child: IndexedStack(
              index: _selectedTab,
              children: [
                _buildLightingControl(),
                _buildClimateControl(),
                _buildScenesControl(),
                _buildDevicesControl(),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildTab(String title, int index) {
    final isSelected = _selectedTab == index;
    
    return Expanded(
      child: InkWell(
        onTap: () => setState(() => _selectedTab = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isSelected
                    ? Theme.of(context).colorScheme.primary
                    : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected
                  ? Theme.of(context).colorScheme.primary
                  : Theme.of(context).textTheme.bodyMedium?.color,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildLightingControl() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Lighting Control',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),
          
          Text('Brightness: ${_lightingBrightness.round()}%'),
          Slider(
            value: _lightingBrightness,
            min: 0,
            max: 100,
            divisions: 100,
            label: '${_lightingBrightness.round()}%',
            onChanged: (value) {
              setState(() => _lightingBrightness = value);
            },
            onChangeEnd: (value) async {
              await _iotRepo.setLighting(
                roomId: 'current-room',
                brightness: value.round(),
              );
            },
          ),
          
          const SizedBox(height: 32),
          
          Text('Color Presets'),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _buildColorButton('Warm', '#FDB462'),
              _buildColorButton('Cool', '#80B0FF'),
              _buildColorButton('Natural', '#FFFFFF'),
              _buildColorButton('Romantic', '#FF8FB1'),
              _buildColorButton('Energize', '#FFD700'),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildColorButton(String label, String color) {
    return ElevatedButton(
      onPressed: () async {
        await _iotRepo.setLighting(
          roomId: 'current-room',
          brightness: _lightingBrightness.round(),
          color: color,
        );
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: Color(
          int.parse(color.substring(1), radix: 16) + 0xFF000000,
        ),
      ),
      child: Text(label),
    );
  }
  
  Widget _buildClimateControl() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Climate Control',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),
          
          Text('Temperature: ${_temperature.round()}°F'),
          Slider(
            value: _temperature,
            min: 65,
            max: 80,
            divisions: 15,
            label: '${_temperature.round()}°F',
            onChanged: (value) {
              setState(() => _temperature = value);
            },
            onChangeEnd: (value) async {
              await _iotRepo.setTemperature(
                roomId: 'current-room',
                temperature: value,
              );
            },
          ),
        ],
      ),
    );
  }
  
  Widget _buildScenesControl() {
    return const Center(child: Text('Scenes - Coming Soon'));
  }
  
  Widget _buildDevicesControl() {
    return const Center(child: Text('Devices - Coming Soon'));
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}
```

**Add to pubspec.yaml**:
```yaml
dependencies:
  table_calendar: ^3.0.9
```

---

### **Days 21-22: Flutter Shop & Concierge**

**File**: `lib/features/shop/data/repositories/shop_repository.dart`
```dart
import '../../../../core/network/api_client.dart';
import '../models/product_model.dart';
import '../models/order_model.dart';

class ShopRepository {
  final ApiClient _apiClient;
  
  ShopRepository(this._apiClient);
  
  Future<List<Product>> getProducts({String? category}) async {
    final response = await _apiClient.get(
      '/shop/products/',
      queryParameters: category != null ? {'category': category} : null,
    );
    
    final List products = response['results'] ?? response;
    return products.map((p) => Product.fromJson(p)).toList();
  }
  
  Future<PickupOrder> createOrder({
    required List<OrderItemData> items,
    String? notes,
  }) async {
    final response = await _apiClient.post(
      '/shop/orders/create_order/',
      data: {
        'items': items.map((item) => item.toJson()).toList(),
        if (notes != null) 'customer_notes': notes,
      },
    );
    
    return PickupOrder.fromJson(response);
  }
  
  Future<List<PickupOrder>> getMyOrders() async {
    final response = await _apiClient.get('/shop/orders/');
    final List orders = response['results'] ?? response;
    return orders.map((o) => PickupOrder.fromJson(o)).toList();
  }
}

class OrderItemData {
  final int productId;
  final int quantity;
  final String? notes;
  
  OrderItemData({
    required this.productId,
    required this.quantity,
    this.notes,
  });
  
  Map<String, dynamic> toJson() => {
    'product_id': productId,
    'quantity': quantity,
    if (notes != null) 'notes': notes,
  };
}
```

---

### **Days 23-24: Flutter Push Notifications**

**File**: `lib/core/services/notification_service.dart`
```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io';

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseBackgroundHandler(RemoteMessage message) async {
  print('Background message: ${message.notification?.title}');
}

class NotificationService {
  static final NotificationService instance = NotificationService._();
  NotificationService._();
  
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = 
      FlutterLocalNotificationsPlugin();
  
  /// Initialize notifications
  Future<void> initialize() async {
    // Request permission (iOS)
    final settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.denied) {
      print('User denied notification permission');
      return;
    }
    
    // Get FCM token
    final token = await _fcm.getToken();
    print('FCM Token: $token');
    // TODO: Send token to backend
    
    // Initialize local notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    final iosSettings = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
    );
    
    final settings = InitializationSettings(
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
    FirebaseMessaging.onBackgroundMessage(firebaseBackgroundHandler);
    
    // Handle notification that opened app
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationOpened);
    
    // Check if app was opened from notification
    final initialMessage = await _fcm.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationOpened(initialMessage);
    }
  }
  
  /// Handle foreground message
  void _handleForegroundMessage(RemoteMessage message) {
    _showLocalNotification(
      title: message.notification?.title ?? 'CoreSync',
      body: message.notification?.body ?? '',
      payload: _encodePayload(message.data),
    );
  }
  
  /// Show local notification
  Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'coresync_default',
      'CoreSync Notifications',
      channelDescription: 'General notifications from CoreSync',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );
    
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload,
    );
  }
  
  /// Handle notification opened
  void _handleNotificationOpened(RemoteMessage message) {
    final data = message.data;
    final type = data['type'];
    
    // Navigate based on type
    switch (type) {
      case 'booking':
        // Navigate to bookings
        break;
      case 'service':
        // Navigate to service
        break;
      case 'order':
        // Navigate to shop order
        break;
      case 'concierge':
        // Navigate to concierge request
        break;
    }
  }
  
  /// Handle local notification tap
  void _onNotificationTapped(NotificationResponse response) {
    final payload = response.payload;
    if (payload != null) {
      final data = _decodePayload(payload);
      // Handle navigation
    }
  }
  
  String _encodePayload(Map<String, dynamic> data) {
    return jsonEncode(data);
  }
  
  Map<String, dynamic> _decodePayload(String payload) {
    try {
      return jsonDecode(payload) as Map<String, dynamic>;
    } catch (e) {
      return {};
    }
  }
  
  /// Update FCM token on backend
  Future<void> updateToken(String token, ApiClient apiClient) async {
    try {
      await apiClient.post(
        '/users/fcm-token/',
        data: {
          'token': token,
          'platform': Platform.isIOS ? 'ios' : 'android',
        },
      );
    } catch (e) {
      print('Failed to update FCM token: $e');
    }
  }
}
```

**Update** `main.dart`:
```dart
import 'package:firebase_core/firebase_core.dart';
import 'core/services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Initialize Notifications
  await NotificationService.instance.initialize();
  
  // ... rest of initialization
  
  runApp(const ProviderScope(child: CoreSyncApp()));
}
```

---

### **Days 25-26: Flutter Testing & Polish**

**File**: `test/features/auth/face_recognition_test.dart`
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:coresync_mobile/features/auth/data/repositories/face_recognition_repository.dart';

void main() {
  group('FaceRecognitionRepository', () {
    late FaceRecognitionRepository repository;
    
    setUp(() {
      repository = FaceRecognitionRepository();
    });
    
    test('should initialize face detector', () {
      expect(repository, isNotNull);
    });
    
    // Add more tests...
  });
}
```

---

## 📅 WEEK 4: APP STORE PREPARATION (Days 27-31)

### **Day 27: iOS App Store Setup**

#### **Step 1: Apple Developer Account**
1. Go to https://developer.apple.com/programs/
2. Enroll ($99/year)
3. Complete company verification (if applicable)

#### **Step 2: App Store Connect**
1. Login: https://appstoreconnect.apple.com/
2. Click "My Apps" → "+" → "New App"
3. Fill information:
   - **Platform**: iOS
   - **Name**: CoreSync
   - **Primary Language**: English (U.S.)
   - **Bundle ID**: life.coresync.coresync
   - **SKU**: CORESYNC001
   - **User Access**: Full Access

#### **Step 3: App Information**
```
Name: CoreSync
Subtitle: Premium Wellness Experience
Category: Primary - Health & Fitness
         Secondary - Lifestyle

App Privacy:
- Privacy Policy URL: https://coresync.life/privacy-policy
- User Privacy Choices URL: https://coresync.life/privacy-policy#choices

Contact Information:
- First Name: CoreSync
- Last Name: Team
- Phone: +1 (551) 574-2281
- Email: info@coresync.life

Copyright: © 2025 CoreSync. All rights reserved.
```

#### **Step 4: Prepare Screenshots**

**Required sizes**:
- 6.7" Display (iPhone 14 Pro Max): 1290 x 2796 pixels
- 6.5" Display (iPhone 11 Pro Max): 1242 x 2688 pixels

**Create 5-8 screenshots showing**:
1. Login with face recognition
2. Home dashboard with portals
3. Booking calendar
4. IoT control panel
5. Service details
6. Membership benefits
7. Shop products
8. Concierge request form

**Tool to create screenshots**:
```bash
# Install
flutter pub global activate screenshots

# Create config
# screenshots.yaml
```

**File**: `screenshots.yaml`
```yaml
screens:
  - login
  - home
  - booking
  - iot
  - shop
  - concierge

devices:
  - iPhone 14 Pro Max
  - iPhone 11 Pro Max

locales:
  - en-US

staging: screenshots/staging
```

**Run**:
```bash
flutter pub global run screenshots:main
```

---

### **Day 28: Android Play Store Setup**

#### **Step 1: Google Play Console**
1. Go to https://play.google.com/console/signup
2. Pay one-time $25 fee
3. Complete account setup

#### **Step 2: Create App**
1. All apps → Create app
2. Fill information:
   - **App name**: CoreSync
   - **Default language**: English (United States)
   - **App or game**: App
   - **Free or paid**: Free

#### **Step 3: App Details**
```
App name: CoreSync
Short description (80 chars):
Premium wellness with AI-powered personalization

Full description (4000 chars):
CoreSync brings the future of wellness to your fingertips...
[Full description from Privacy & policy page]

App category: Health & Fitness
Tags: wellness, spa, meditation, luxury

Contact details:
- Email: info@coresync.life
- Phone: +15515742281
- Website: https://coresync.life

Privacy Policy: https://coresync.life/privacy-policy
```

#### **Step 4: Content Rating**
Complete the questionnaire:
- Violence: None
- Sexual content: None
- Nudity: None (spa environment context)
- Profanity: None
- Drugs: None (wellness products)
- Gambling: None

Expected rating: **Everyone**

#### **Step 5: Store Listing Assets**

**Required**:
- App icon: 512 x 512 pixels (PNG, 32-bit)
- Feature graphic: 1024 x 500 pixels (JPG or PNG)
- Phone screenshots: minimum 2, maximum 8

**Create feature graphic** (promotional banner):
- CoreSync logo
- Tagline: "Premium Wellness Experience"
- Key features: Face Recognition • AI Massage • IoT Control

---

### **Day 29: Deep Links Setup**

#### **iOS Universal Links**

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
          "/membership/*",
          "/shop/*",
          "/concierge/*",
          "/dashboard/*"
        ]
      }
    ]
  },
  "webcredentials": {
    "apps": ["TEAM_ID.life.coresync.coresync"]
  },
  "appclips": {
    "apps": []
  }
}
```

**Update** `ios/Runner/Info.plist`:
```xml
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:coresync.life</string>
    <string>applinks:www.coresync.life</string>
</array>
```

#### **Android App Links**

**File**: `coresync_backend/static/.well-known/assetlinks.json`
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "life.coresync.coresync",
    "sha256_cert_fingerprints": [
      "REPLACE_WITH_YOUR_SHA256_FROM_KEYSTORE"
    ]
  }
}]
```

**Get SHA256 fingerprint**:
```bash
# Create release keystore
keytool -genkey -v -keystore ~/coresync-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias coresync \
  -storepass STRONG_PASSWORD \
  -keypass STRONG_PASSWORD

# Get SHA256
keytool -list -v -keystore ~/coresync-release.jks \
  -alias coresync -storepass STRONG_PASSWORD | grep SHA256
```

**Create**: `android/key.properties`
```properties
storePassword=YOUR_STRONG_PASSWORD
keyPassword=YOUR_STRONG_PASSWORD
keyAlias=coresync
storeFile=/Users/USERNAME/coresync-release.jks
```

**Update**: `android/app/build.gradle`
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    // ...
    
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
        }
    }
}
```

**Update**: `android/app/src/main/AndroidManifest.xml`
```xml
<activity android:name=".MainActivity">
    <!-- Deep Links -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="https" android:host="coresync.life"/>
        <data android:scheme="https" android:host="www.coresync.life"/>
    </intent-filter>
    
    <!-- Custom URL Scheme -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="coresync"/>
    </intent-filter>
</activity>
```

**Serve from Django**:

**Update** `config/urls.py`:
```python
from django.views.static import serve

urlpatterns = [
    # ... existing ...
    
    # Well-known files for App Links
    path('.well-known/apple-app-site-association', 
         serve, 
         {'document_root': settings.STATIC_ROOT, 
          'path': '.well-known/apple-app-site-association'},
         name='apple-app-site-association'),
    path('.well-known/assetlinks.json',
         serve,
         {'document_root': settings.STATIC_ROOT,
          'path': '.well-known/assetlinks.json'},
         name='assetlinks'),
]
```

---

### **Day 30-31: Build & Test Apps**

#### **iOS Build**
```bash
cd /Users/olegbonislavskyi/SPA-AI/coresync_mobile

# Clean
flutter clean
flutter pub get

# Generate code
flutter pub run build_runner build --delete-conflicting-outputs

# Build iOS
flutter build ios --release --no-codesign

# Open Xcode for signing and upload
open ios/Runner.xcworkspace
```

**In Xcode**:
1. Select Runner → Signing & Capabilities
2. Select your Team
3. Enable "Automatically manage signing"
4. Product → Archive
5. Distribute App → App Store Connect
6. Upload

#### **Android Build**
```bash
# Build app bundle
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab

# Test locally (optional)
flutter build apk --release
flutter install
```

---

## 📅 WEEK 5: TESTING & OPTIMIZATION (Days 32-35)

### **Day 32: Backend Testing**

**File**: `coresync_backend/test_suite.py`
```python
"""
Comprehensive test suite for CoreSync backend.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from services.models import Service, ServiceCategory
from shop.models import Product, PickupOrder
from concierge.models import ConciergeRequest

User = get_user_model()

class ShopAPITestCase(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category='skincare',
            description='Test',
            short_description='Test',
            price=100.00,
            member_price=80.00,
            stock=10,
        )
    
    def test_list_products(self):
        response = self.client.get('/api/shop/products/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['results']), 0)
    
    def test_create_order(self):
        data = {
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2,
                }
            ]
        }
        response = self.client.post(
            '/api/shop/orders/create_order/',
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('order_number', response.json())
    
    def test_stock_decreases_after_order(self):
        initial_stock = self.product.stock
        
        data = {
            'items': [{'product_id': self.product.id, 'quantity': 2}]
        }
        self.client.post(
            '/api/shop/orders/create_order/',
            data,
            content_type='application/json'
        )
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)

class BookingAPITestCase(APITestCase):
    # Similar tests for booking system
    pass

class ConciergeAPITestCase(APITestCase):
    # Similar tests for concierge system
    pass
```

**Run tests**:
```bash
python manage.py test
```

---

### **Day 33: Frontend Testing**

**Manual testing checklist**:

**Cross-Browser**:
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + mobile)
- [ ] Firefox
- [ ] Edge

**Pages to test**:
- [ ] Home - hero video, navigation
- [ ] Services - list, detail, booking
- [ ] Shop - products, cart, checkout
- [ ] Concierge - form submission
- [ ] Membership - pricing tables
- [ ] Dashboard - all 6 pages
- [ ] Legal - all 3 pages
- [ ] Auth - login, signup, reset

**Functionality**:
- [ ] Forms submit correctly
- [ ] API calls work
- [ ] Toast notifications appear
- [ ] Mobile menu works
- [ ] Calendar booking works
- [ ] Shop cart persists
- [ ] Navigation smooth

---

### **Day 34: Mobile App Testing**

**Device Testing**:
- [ ] iPhone 12 (iOS 16+)
- [ ] iPhone 14 Pro (iOS 17+)
- [ ] iPad Pro (optional)
- [ ] Pixel 6 (Android 13+)
- [ ] Samsung Galaxy S22 (Android 14+)

**Feature Testing**:
- [ ] Face registration (3 captures)
- [ ] Face authentication (>85% match)
- [ ] Booking flow (end-to-end)
- [ ] IoT controls (all tabs)
- [ ] Shop (browse, add to cart, order)
- [ ] Concierge (submit request, view status)
- [ ] Push notifications (receive, tap)
- [ ] Deep links (open from browser)

**Performance Testing**:
```bash
# Profile app
flutter run --profile

# Check app size
flutter build apk --analyze-size
flutter build appbundle --analyze-size
```

**Targets**:
- App size: < 50 MB
- Cold start: < 3 seconds
- Frame rate: 60 FPS
- Memory usage: < 200 MB

---

### **Day 35: Performance Optimization**

#### **Website Optimization**

**Image Optimization**:
```bash
# Install ImageMagick
brew install imagemagick

# Optimize PNGs
cd coresync_backend/static/images
for file in *.png; do
    convert "$file" -resize '1920x1080>' -quality 85 "optimized_$file"
done

# Convert to WebP
for file in *.png *.jpg; do
    cwebp -q 85 "$file" -o "${file%.*}.webp"
done
```

**CSS/JS Minification**:
```bash
# Install tools
npm install -g clean-css-cli terser

# Minify CSS
cd static/css
cleancss -o styles.min.css styles.css
cleancss -o dashboard.min.css dashboard.css

# Minify JS
cd ../js
terser dashboard.js -o dashboard.min.js --compress --mangle
terser shop.js -o shop.min.js --compress --mangle
terser concierge.js -o concierge.min.js --compress --mangle
```

**Update templates to use minified**:
```html
{% if not DEBUG %}
    <link rel="stylesheet" href="{% static 'css/styles.min.css' %}">
    <script src="{% static 'js/dashboard.min.js' %}"></script>
{% else %}
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    <script src="{% static 'js/dashboard.js' %}"></script>
{% endif %}
```

#### **Django Settings for Production**

**Update** `config/settings.py`:
```python
# Production optimizations
if not DEBUG:
    # Static files compression
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Database connection pooling
    DATABASES['default']['CONN_MAX_AGE'] = 600
    
    # Caching
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'coresync',
            'TIMEOUT': 300,
        }
    }
    
    # Session in cache
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
```

---

## 📅 WEEK 6: DEPLOYMENT & LAUNCH (Days 36-42)

### **Day 36: Backend Production Deployment**

#### **Render.com Setup**

**File**: `render.yaml` (update existing)
```yaml
services:
  # Web Service
  - type: web
    name: coresync-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120"
    healthCheckPath: /health/
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.0
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: coresync-db
          property: connectionString
      - key: REDIS_URL
        fromDatabase:
          name: coresync-redis
          property: connectionString
      - key: ALLOWED_HOSTS
        value: coresync.life,www.coresync.life,*.onrender.com
      - key: STRIPE_PUBLISHABLE_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false

databases:
  - name: coresync-db
    databaseName: coresync_prod
    user: coresync
    plan: starter
    region: oregon

  - name: coresync-redis
    plan: starter
    region: oregon
```

**Environment Variables to set manually**:
```bash
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
QUICKBOOKS_CLIENT_ID=...
QUICKBOOKS_CLIENT_SECRET=...
GA_MEASUREMENT_ID=G-...
EMAIL_HOST_USER=info@coresync.life
EMAIL_HOST_PASSWORD=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=coresync-media
SENTRY_DSN=https://...
```

**Deploy**:
```bash
git add .
git commit -m "Production deployment ready"
git push origin main

# Render will auto-deploy from GitHub
```

---

### **Day 37: Domain & DNS Setup**

#### **GoDaddy DNS Configuration**

Login to GoDaddy → My Domains → coresync.life → DNS Management

**Add records**:
```
Type    Name    Value                               TTL
A       @       <RENDER_IP_FROM_DASHBOARD>         600
A       www     <RENDER_IP_FROM_DASHBOARD>         600
CNAME   api     coresync-backend.onrender.com      3600
TXT     @       v=spf1 include:_spf.google.com ~all 3600
```

**Get Render IP**:
- Go to Render Dashboard → coresync-backend → Settings → Custom Domain
- Add: coresync.life
- Copy the IP address shown

**Update Django settings**:
```python
ALLOWED_HOSTS = [
    'coresync.life',
    'www.coresync.life',
    'api.coresync.life',
    '*.onrender.com',
]

# Force HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
```

**SSL Certificate**: Render provides automatic Let's Encrypt SSL

---

### **Day 38: SEO & Analytics**

#### **Google Analytics 4 Setup**

1. Go to https://analytics.google.com/
2. Create account → Create property
3. Property name: CoreSync
4. Get Measurement ID (G-XXXXXXXXXX)

**Update** `templates/base.html`:
```html
<head>
    <!-- ... existing meta tags ... -->
    
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_MEASUREMENT_ID }}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '{{ GA_MEASUREMENT_ID }}', {
            'send_page_view': true,
            'anonymize_ip': true
        });
    </script>
    
    <!-- SEO Meta Tags -->
    <meta name="description" content="{% block description %}Brooklyn's most advanced spa featuring AI-powered massage beds, meditation pods, and immersive wellness experiences.{% endblock %}">
    <meta name="keywords" content="luxury spa brooklyn, wellness center, AI massage, meditation, premium spa, mens spa, couples spa, coresync">
    <meta name="author" content="CoreSync">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}CoreSync - Premium Wellness Experience{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Brooklyn's most advanced spa{% endblock %}">
    <meta property="og:image" content="https://coresync.life{% static 'images/og-image.jpg' %}">
    <meta property="og:url" content="https://coresync.life{{ request.path }}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="CoreSync">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{% block twitter_title %}CoreSync{% endblock %}">
    <meta name="twitter:description" content="{% block twitter_description %}Premium Wellness Experience{% endblock %}">
    <meta name="twitter:image" content="https://coresync.life{% static 'images/twitter-card.jpg' %}">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="https://coresync.life{{ request.path }}">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": "CoreSync",
        "description": "Premium wellness spa with AI-powered technology",
        "url": "https://coresync.life",
        "logo": "https://coresync.life{% static 'images/logo.png' %}",
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
        "priceRange": "$$$",
        "openingHours": "Mo-Su 09:00-22:00"
    }
    </script>
</head>
```

#### **Sitemap.xml**

**File**: `templates/sitemap.xml`
```xml
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
    <url>
        <loc>https://coresync.life/shop/</loc>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://coresync.life/book/</loc>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://coresync.life/private/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://coresync.life/menssuite/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://coresync.life/about/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://coresync.life/technologies/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://coresync.life/contacts/</loc>
        <changefreq>yearly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://coresync.life/privacy-policy/</loc>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://coresync.life/terms/</loc>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://coresync.life/refund-policy/</loc>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
</urlset>
```

**Add URL**:
```python
# config/urls.py
urlpatterns = [
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml',
        content_type='application/xml'
    ), name='sitemap'),
]
```

#### **robots.txt**

**File**: `static/robots.txt`
```txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dashboard/
Disallow: /api/

Sitemap: https://coresync.life/sitemap.xml
```

---

### **Day 39: Monitoring & Logging**

#### **Sentry Setup**

**Install**:
```bash
pip install sentry-sdk
```

**Configure** `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
        release=f"coresync-backend@{os.environ.get('GIT_COMMIT', 'unknown')}",
    )
```

**Flutter Sentry**:

**Update** `main.dart`:
```dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = 'YOUR_SENTRY_DSN';
      options.tracesSampleRate = 0.1;
      options.environment = 'production';
    },
    appRunner: () => runApp(const ProviderScope(child: CoreSyncApp())),
  );
}
```

#### **Logging Configuration**

**File**: `config/logging_config.py`
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'ERROR',
            'propagate': False,
        },
        'coresync': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

### **Day 40: App Store Submission**

#### **Final iOS Checklist**

**App Store Connect**:
1. Go to "App Information"
2. Fill all required fields
3. Upload screenshots (6.7" and 6.5")
4. Add app preview video (optional)

**Version Information**:
```
Version: 1.0.0
Copyright: © 2025 CoreSync
Category: Health & Fitness
Age Rating: 4+
```

**App Description**:
```
CoreSync brings the future of wellness to your fingertips. Brooklyn's most advanced spa experience featuring:

🤖 AI-Powered Personalization
• Face recognition for instant access
• Smart booking recommendations
• Personalized wellness insights

🧘 Advanced Technology
• Control AI massage beds remotely
• Start meditation sessions from anywhere
• Customize immersive screen experiences
• Adjust lighting, temperature, and scents

📅 Effortless Booking
• Real-time availability
• One-tap booking
• Priority member access
• Pre-select programs and add-ons

💎 Exclusive Benefits
• Mensuite - Men's spa access
• Coresync Private - Couple's experiences
• Unlimited - Full access to all amenities

🛍️ Curated Shop
• Premium wellness products
• Convenient spa pickup
• Member-exclusive pricing

👑 Personal Concierge
• Special item requests
• Premium goods sourcing
• Next-visit delivery

Membership required. Visit coresync.life for details.
```

**Keywords**:
```
spa, wellness, meditation, massage, luxury spa, brooklyn, face recognition, AI massage, iot control, wellness technology, premium spa, couples spa, mens spa, biometric
```

**Support & Privacy URLs**:
```
Support: https://coresync.life/contacts
Privacy: https://coresync.life/privacy-policy
Terms: https://coresync.life/terms
```

**Build and Upload**:
```bash
cd coresync_mobile

# Final build
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
flutter build ios --release

# Open Xcode
open ios/Runner.xcworkspace

# In Xcode:
# Product → Archive
# Window → Organizer
# Distribute App → App Store Connect → Upload
```

**Submit for Review**:
1. Select build in App Store Connect
2. Fill "What's New in This Version"
3. Add demo account credentials
4. Submit for Review

**Demo Account for Reviewers**:
```
Email: demo@coresync.life
Password: ReviewDemo2025!

Notes for Reviewer:
- This is a premium spa membership app
- Demo account has active Premium membership
- Face recognition can be skipped for testing
- IoT features use demo mode without physical devices
- All features are testable with demo account
```

---

### **Day 41: Play Store Submission**

#### **Final Android Checklist**

**Store Listing**:
```
Title: CoreSync
Short description (80 chars):
Premium wellness with AI-powered personalization and IoT control

Full description (4000 chars):
[Same as iOS]

Category: Health & Fitness
Tags: wellness, spa, meditation, massage, luxury
Email: info@coresync.life
Phone: +15515742281
Website: https://coresync.life
Privacy Policy: https://coresync.life/privacy-policy
```

**Content Rating**: Complete questionnaire → Expected: Everyone

**Build and Upload**:
```bash
cd coresync_mobile

# Final build
flutter clean
flutter pub get
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab
```

**Upload to Play Console**:
1. Production → Create new release
2. Upload app-release.aab
3. Fill release notes
4. Add countries (United States, or Worldwide)
5. Review and rollout

**Release Notes**:
```
🎉 Welcome to CoreSync v1.0

Experience Brooklyn's most advanced wellness spa:
• Face recognition login
• AI-powered service recommendations  
• One-tap booking
• IoT device control
• Personal concierge service
• Premium spa shop

Membership required. Visit coresync.life to join.
```

---

### **Day 42: Final Checks & Launch**

#### **Pre-Launch Checklist**

**Backend**:
- [ ] Production deployed on Render
- [ ] Database migrations run
- [ ] Static files collected
- [ ] SSL certificate active
- [ ] Health check responding
- [ ] API endpoints working
- [ ] Admin panel accessible
- [ ] Stripe webhooks configured
- [ ] Error monitoring active (Sentry)
- [ ] Backups configured

**Frontend**:
- [ ] All 23 pages live
- [ ] All links working
- [ ] Forms submitting
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Fast load times (<3s)
- [ ] SEO meta tags complete
- [ ] GA4 tracking active
- [ ] sitemap.xml accessible
- [ ] robots.txt configured

**Mobile Apps**:
- [ ] iOS build uploaded to TestFlight
- [ ] Android build uploaded to Internal Testing
- [ ] Both apps submitted for review
- [ ] Screenshots uploaded
- [ ] Descriptions complete
- [ ] Privacy policies linked
- [ ] Demo accounts provided
- [ ] Deep links tested

**Final Tests**:
- [ ] Create real booking (end-to-end)
- [ ] Process test payment
- [ ] Submit shop order
- [ ] Submit concierge request
- [ ] Test face recognition (mobile)
- [ ] Test IoT controls (mobile)
- [ ] Receive push notification
- [ ] Test deep link from web to app

---

## 🎉 POST-LAUNCH (Week 7+)

### **What Remains After 99%**

**From Client**:
1. **Video Content** (3-5 professional videos)
   - Morning hero video (energizing)
   - Afternoon hero video (relaxing)
   - Evening hero video (calming)
   - Equipment demo videos

2. **IoT API Keys & Documentation**
   - AI Massage Bed API credentials
   - Meditation Pod integration keys
   - Immersive Screen API docs
   - Smart Mirror connection details
   - Lighting system API

3. **Professional Photos**
   - Team members
   - Facility rooms
   - Equipment close-ups
   - Treatment room photos
   - Product photography

4. **Content**
   - Service descriptions (detailed)
   - Product descriptions
   - About Us copy
   - Team member bios

**App Store Review**:
- **iOS**: 24-48 hours typically
- **Android**: 1-7 days typically

**Then**: 🚀 **FULL LAUNCH!**

---

## 📋 DELIVERABLES AT 99%

### **Website** (23 pages)
✅ All pages complete and functional
✅ Clean, maintainable code
✅ SEO optimized
✅ Mobile responsive
✅ Production deployed

### **Backend API**
✅ 100% functional endpoints
✅ Stripe payments integrated
✅ QuickBooks ready
✅ Professional admin panel
✅ Secure and scalable

### **Mobile App**
✅ Face recognition working
✅ Real-time booking
✅ IoT control interface
✅ Shop & Concierge features
✅ Push notifications
✅ Submitted to stores

### **Infrastructure**
✅ Production server (Render)
✅ Custom domain (coresync.life)
✅ SSL certificates
✅ Monitoring (Sentry)
✅ Analytics (GA4)
✅ Backups configured

---

## 💰 COSTS BREAKDOWN

### **One-Time**
- Apple Developer: $99/year
- Google Play Developer: $25 (lifetime)
- Domain (already owned): $0

### **Monthly**
- Render.com (Starter): $25-50
- AWS S3 (media): $5-10
- Firebase (Free tier): $0
- Sentry (Free tier): $0

**Total Monthly**: ~$35-65

---

## 🎯 SUCCESS METRICS

### **Technical Quality**
- Code Quality: 10/10
- Test Coverage: >80%
- Performance Score: >90
- SEO Score: >95
- Accessibility: AA compliant

### **Functionality**
- All features working: 100%
- API uptime: 99.9%
- Mobile app crash-free: >99%
- Page load time: <2s

### **Readiness**
- Backend: 100% ✅
- Frontend: 100% ✅
- Mobile: 100% ✅
- Deployment: 100% ✅

**Status**: READY FOR FULL LAUNCH after video content + IoT setup! 🚀

---

## 📞 SUPPORT CONTACTS

**Development Questions**: Check code comments and documentation  
**Deployment Issues**: Render.com support  
**App Store Issues**: Apple Developer support  
**Play Store Issues**: Google Play support  
**Payment Issues**: Stripe support  

**Emergency**: info@coresync.life

---

**END OF 42-DAY PLAN - READY TO EXECUTE! 🎉**

