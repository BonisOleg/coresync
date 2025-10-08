# 🚀 CORESYNC - ПОКРАЩЕНИЙ SENIOR ПЛАН ДО 99%

**Дата створення**: October 8, 2025  
**Версія**: 2.0 (Enhanced after deep code analysis)  
**Статус проекту**: 75% → 99% готовності

---

## 📊 EXECUTIVE SUMMARY - ДЕТАЛЬНИЙ АНАЛІЗ

### **ЩО Я ЗНАЙШОВ (Глибокий аналіз коду)**

#### ✅ **BACKEND - ВІДМІННА ЯКІСТЬ (90% готово)**

**Models (Professional Senior Level)**:
```python
✅ services/models.py (227 lines) - повністю готово
   - Service, ServiceCategory, ServiceAddon, ServiceHistory
   - Ціноутворення: member_price, non_member_price
   - Gallery images as JSONField
   
✅ services/booking_models.py (481 lines!) - професійний рівень
   - Booking з priority logic
   - Room з IoT device IDs
   - AvailabilitySlot з member_only_until
   - BookingAddon through model
   - QuickBooks sync готовий
   
✅ memberships/models.py (209 lines) - готово
   - MembershipPlan з benefits JSON
   - Membership з usage tracking
   - Priority booking logic
   
✅ users/models.py (131 lines) - готово
   - Face recognition data field
   - UserPreference для IoT
   - Emergency contact
   
✅ iot_control/models.py (249 lines) - готово
   - IoTDevice з network config
   - Scene з device_settings JSON
   - ControlLog для security
   - SensorReading для analytics
   
✅ payments/models.py (199 lines) - готово
   - Payment з Stripe + QuickBooks
   - StripeWebhookEvent
   - QuickBooksSync з retry logic
```

**Views (Professional Implementation)**:
```python
✅ services/views.py - повністю функціональні ViewSets
   - ServiceViewSet з фільтрами та пошуком
   - Кешування (15 min для categories)
   - Custom actions: mensuite(), featured()
   
✅ services/booking_views.py (540 lines!) - просто WOW
   - BookingViewSet з member priority
   - availability() endpoint - складна логіка
   - create_booking() - повна валідація
   - my_bookings(), cancel_booking()
   - _get_max_advance_days() - 3/30/60/90 days
   - QuickBooks integration готова
```

**❌ Відсутні apps (потрібно створити)**:
- Shop app (Product, PickupOrder models)
- Concierge app (ConciergeRequest model)

---

#### 📱 **FLUTTER - ВІДМІННА СТРУКТУРА, АЛЕ ПОРОЖНЯ (30% готово)**

**Архітектура**:
```
✅ Clean Architecture структура готова
✅ 24 .dart файли створені
✅ Theme професійний (640 lines!)
✅ API client готовий (Dio + secure storage)
✅ Packages всі підключені (pubspec.yaml)

❌ Більшість файлів порожні або placeholder
❌ Немає реалізації features
❌ Немає integration з API
```

**Flutter pubspec.yaml Analysis**:
```yaml
✅ Face recognition: google_mlkit_face_detection: ^0.9.0
✅ Camera: camera: ^0.10.5+5
✅ Biometrics: local_auth: ^2.1.7, biometric_storage: ^5.0.0
✅ IoT: flutter_bluetooth_serial, wifi_iot
✅ Payments: stripe_payment, pay, in_app_purchase
✅ Push: firebase_messaging, flutter_local_notifications
✅ State: provider, riverpod
✅ Navigation: go_router, auto_route
✅ Network: dio, retrofit, socket_io_client
```

**Висновок**: Packages є, структура є, код потрібно писати!

---

#### 🌐 **WEBSITE - ЧИСТИЙ КОД (70% готово)**

**Аналіз якості**:
```bash
✅ Немає inline стилів (grep результат: 0 matches) - PERFECT!
✅ Тільки 14 !important (styles.css: 8, membership.css: 6) - МІНІМУМ!
✅ 13 сторінок готові
❌ 10 сторінок відсутні (43%)

Готові сторінки:
1. index.html - Hero з відео
2. private.html - Couple spa
3. menssuite.html - Men's spa
4. membership.html - Pricing tables
5. contacts.html - Contact form
6. booking_calendar.html - Calendar
7. pages/about.html - Brand story
8. pages/technologies.html - Tech showcase
9. services/list.html - Services grid
10. services/detail.html - Service page
11-13. auth/*.html - Login/Signup/Reset (3 files)
14-19. dashboard/*.html - Dashboard pages (6 files)
```

**Відсутні сторінки** (критично):
```
❌ shop/index.html + shop/cart.html
❌ concierge/request.html
❌ dashboard/membership_detail.html (enhance existing)
❌ legal/privacy_policy.html
❌ legal/terms.html
❌ legal/refund_policy.html
```

---

## 🎯 ПОКРАЩЕНИЙ ПЛАН - 7 ТИЖНІВ ДО 99%

### **PHASE 1: BACKEND + WEBSITE COMPLETION (Week 1-2)**

#### **Week 1, Days 1-3: Missing Backend Apps**

##### **Day 1: Shop App**
```bash
cd coresync_backend
python manage.py startapp shop
```

**File**: `shop/models.py`
```python
from django.db import models
from core.models import BaseModel

class Product(BaseModel):
    CATEGORIES = (
        ('skincare', 'Skincare'),
        ('wellness', 'Wellness Tech'),
        ('accessories', 'Accessories'),
        ('supplements', 'Supplements'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    member_price = models.DecimalField(max_digits=10, decimal_places=2)
    member_discount_percent = models.PositiveIntegerField(default=10)
    
    # Inventory
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    
    # Media
    main_image = models.ImageField(upload_to='products/')
    gallery_images = models.JSONField(default=list)
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # QuickBooks integration
    quickbooks_item_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'shop_products'
        ordering = ['category', 'name']

class PickupOrder(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='pickup_orders')
    
    # Pickup details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_date = models.DateField(blank=True, null=True)
    pickup_booking = models.ForeignKey(
        'services.Booking', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Link to booking for pickup"
    )
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)
    
    # QuickBooks
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_invoice_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'pickup_orders'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            year = timezone.now().year
            count = PickupOrder.objects.filter(
                order_number__startswith=f'PO-{year}-'
            ).count() + 1
            self.order_number = f'PO-{year}-{count:06d}'
        super().save(*args, **kwargs)

class OrderItem(BaseModel):
    order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    notes = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'order_items'
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
```

**File**: `shop/serializers.py`
```python
from rest_framework import serializers
from .models import Product, PickupOrder, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    savings_amount = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 'short_description',
            'price', 'member_price', 'savings_amount', 'discount_percentage',
            'stock', 'in_stock', 'main_image', 'gallery_images',
            'is_featured', 'is_active'
        ]
    
    def get_savings_amount(self, obj):
        return obj.price - obj.member_price
    
    def get_discount_percentage(self, obj):
        if obj.price > 0:
            return round(((obj.price - obj.member_price) / obj.price) * 100, 1)
        return 0
    
    def get_in_stock(self, obj):
        return obj.stock > 0

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.main_image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'unit_price', 'total_price', 'notes']

class PickupOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = PickupOrder
        fields = [
            'id', 'order_number', 'customer_name', 'status', 'pickup_date',
            'subtotal', 'tax', 'total', 'items', 'customer_notes',
            'created_at', 'paid_at'
        ]
```

**File**: `shop/views.py`
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q
from .models import Product, PickupOrder, OrderItem
from .serializers import ProductSerializer, PickupOrderSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('category', 'name')

class PickupOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PickupOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PickupOrder.objects.filter(user=self.request.user).prefetch_related('items')
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create pickup order from cart"""
        try:
            items_data = request.data.get('items', [])
            if not items_data:
                return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create order
            order = PickupOrder.objects.create(
                user=request.user,
                customer_notes=request.data.get('notes', '')
            )
            
            # Add items
            subtotal = 0
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = item_data['quantity']
                
                # Use member price if user is member
                if hasattr(request.user, 'membership') and request.user.membership.is_active:
                    unit_price = product.member_price
                else:
                    unit_price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                subtotal += unit_price * quantity
            
            # Calculate totals
            tax = subtotal * 0.08  # 8% tax (adjust as needed)
            order.subtotal = subtotal
            order.tax = tax
            order.total = subtotal + tax
            order.save()
            
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

**File**: `shop/urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, PickupOrderViewSet

router = DefaultRouter()
router.register(r'shop/products', ProductViewSet, basename='product')
router.register(r'shop/orders', PickupOrderViewSet, basename='pickup-order')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

**Add to** `config/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'shop',  # Add this
]
```

**Add to** `config/urls.py`:
```python
urlpatterns = [
    # ...
    path('', include('shop.urls')),  # Shop API
]
```

---

##### **Day 2: Concierge App**
```bash
python manage.py startapp concierge
```

**File**: `concierge/models.py`
```python
from django.db import models
from core.models import BaseModel

class ConciergeRequest(BaseModel):
    REQUEST_TYPES = (
        ('alcohol', 'Premium Alcohol'),
        ('flowers', 'Fresh Flowers'),
        ('food', 'Gourmet Food'),
        ('jewelry', 'Jewelry & Accessories'),
        ('luxury', 'Luxury Items'),
        ('gift', 'Gift Items'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )
    
    request_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='concierge_requests')
    
    # Request details
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200, help_text="Brief title of the request")
    description = models.TextField(help_text="Detailed description")
    product_link = models.URLField(blank=True, help_text="Optional link to product")
    
    # Budget and pricing
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    
    # Scheduling
    preferred_pickup_date = models.DateField()
    pickup_booking = models.ForeignKey(
        'services.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Link to booking for pickup"
    )
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Staff notes
    admin_notes = models.TextField(blank=True, help_text="Internal staff notes")
    decline_reason = models.TextField(blank=True)
    
    # Member verification
    requires_age_verification = models.BooleanField(default=False, help_text="For alcohol purchases")
    age_verified = models.BooleanField(default=False)
    
    # Payment
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # QuickBooks
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_invoice_id = models.CharField(max_length=100, blank=True)
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True, help_text="Photos or reference images")
    
    class Meta:
        db_table = 'concierge_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'preferred_pickup_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            from django.utils import timezone
            year = timezone.now().year
            count = ConciergeRequest.objects.filter(
                request_number__startswith=f'CR-{year}-'
            ).count() + 1
            self.request_number = f'CR-{year}-{count:06d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_number} - {self.user.full_name} - {self.title}"
    
    @property
    def is_within_budget(self):
        """Check if actual cost is within budget"""
        if self.actual_cost > 0:
            return self.budget_min <= self.actual_cost <= self.budget_max
        return True
    
    @property
    def can_be_approved(self):
        """Check if request can be approved"""
        return self.status == 'pending'
    
    @property
    def can_be_cancelled(self):
        """Check if request can be cancelled by user"""
        return self.status in ['pending', 'approved', 'processing']
```

**File**: `concierge/serializers.py`
```python
from rest_framework import serializers
from .models import ConciergeRequest

class ConciergeRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = ConciergeRequest
        fields = [
            'id', 'request_number', 'user_name', 'request_type', 'request_type_display',
            'title', 'description', 'product_link', 'budget_min', 'budget_max',
            'actual_cost', 'preferred_pickup_date', 'status', 'status_display',
            'submitted_at', 'admin_notes', 'can_cancel', 'paid_at'
        ]
        read_only_fields = ['request_number', 'submitted_at', 'actual_cost', 'admin_notes']
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled()
```

**File**: `concierge/views.py`
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ConciergeRequest
from .serializers import ConciergeRequestSerializer

class ConciergeRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ConciergeRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConciergeRequest.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel_request(self, request, pk=None):
        """Cancel a concierge request"""
        concierge_request = self.get_object()
        
        if not concierge_request.can_be_cancelled():
            return Response({
                'error': 'This request cannot be cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        concierge_request.status = 'cancelled'
        concierge_request.save()
        
        return Response({
            'message': 'Request cancelled successfully',
            'request_number': concierge_request.request_number
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending requests"""
        pending_requests = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
```

**File**: `concierge/urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConciergeRequestViewSet

router = DefaultRouter()
router.register(r'concierge/requests', ConciergeRequestViewSet, basename='concierge-request')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

**Add to** `config/settings.py` and `config/urls.py` (same as Shop)

---

##### **Day 3: Run Migrations & Admin**

```bash
# Create migrations
python manage.py makemigrations shop concierge

# Run migrations
python manage.py migrate

# Create superuser if not exists
python manage.py createsuperuser
```

**File**: `shop/admin.py`
```python
from django.contrib import admin
from .models import Product, PickupOrder, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'member_price', 'stock', 'is_active']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(PickupOrder)
class PickupOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'pickup_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__email']
    inlines = [OrderItemInline]
```

**File**: `concierge/admin.py`
```python
from django.contrib import admin
from .models import ConciergeRequest

@admin.register(ConciergeRequest)
class ConciergeRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'user', 'title', 'request_type', 'status', 'budget_max', 'preferred_pickup_date']
    list_filter = ['status', 'request_type', 'submitted_at']
    search_fields = ['request_number', 'user__email', 'title', 'description']
    readonly_fields = ['request_number', 'submitted_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'user', 'request_type', 'title', 'description', 'product_link')
        }),
        ('Budget & Pricing', {
            'fields': ('budget_min', 'budget_max', 'actual_cost')
        }),
        ('Schedule & Pickup', {
            'fields': ('preferred_pickup_date', 'pickup_booking')
        }),
        ('Status & Processing', {
            'fields': ('status', 'submitted_at', 'reviewed_at', 'completed_at', 'admin_notes', 'decline_reason')
        }),
        ('Payment', {
            'fields': ('payment', 'paid_at', 'quickbooks_synced', 'quickbooks_invoice_id')
        }),
    )
```

---

#### **Week 1, Days 4-7: Website Pages**

##### **Day 4: Shop Pages**

**File**: `templates/shop/index.html`
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Curated Spa Shop - CoreSync{% endblock %}

{% block content %}
<!-- Hero Section -->
<section class="hero-section" style="padding: 8rem 0 4rem;">
    <div class="container">
        <h1 class="heading-xlarge">Curated Spa Shop</h1>
        <p class="body-large" style="max-width: 600px; margin: 2rem auto;">
            Premium wellness products, ready for pickup on your next visit
        </p>
    </div>
</section>

<!-- Categories Filter -->
<section class="section">
    <div class="container">
        <div class="filter-buttons" style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-bottom: 3rem;">
            <button class="btn-secondary filter-btn active" data-category="all">All Products</button>
            <button class="btn-secondary filter-btn" data-category="skincare">Skincare</button>
            <button class="btn-secondary filter-btn" data-category="wellness">Wellness Tech</button>
            <button class="btn-secondary filter-btn" data-category="accessories">Accessories</button>
            <button class="btn-secondary filter-btn" data-category="supplements">Supplements</button>
        </div>

        <!-- Products Grid -->
        <div class="products-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem;">
            <!-- Products will be loaded dynamically via JavaScript -->
        </div>

        <!-- Pickup Notice -->
        <div class="pickup-notice" style="background: rgba(255,255,255,0.05); padding: 2rem; margin-top: 4rem; border-radius: 8px; text-align: center;">
            <h3>💝 Pickup Only</h3>
            <p>All products are prepared and waiting for you on your next spa visit. No shipping required!</p>
        </div>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/shop.js' %}"></script>
{% endblock %}
```

**File**: `templates/shop/cart.html`
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Your Pickup List - CoreSync{% endblock %}

{% block content %}
<section class="section" style="padding-top: 8rem;">
    <div class="container" style="max-width: 1000px;">
        <h1 class="heading-large">Your Pickup List</h1>
        
        <div id="cart-items" style="margin: 3rem 0;">
            <!-- Cart items loaded via JavaScript -->
        </div>

        <div class="cart-summary" style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 8px;">
            <div class="summary-row" style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <span>Subtotal:</span>
                <span id="subtotal">$0.00</span>
            </div>
            <div class="summary-row" style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <span>Tax (8%):</span>
                <span id="tax">$0.00</span>
            </div>
            <div class="summary-row" style="display: flex; justify-content: space-between; font-size: 1.5rem; font-weight: bold; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <span>Total:</span>
                <span id="total">$0.00</span>
            </div>

            <form id="checkout-form" style="margin-top: 2rem;">
                <label class="form-label">Pickup Notes (optional)</label>
                <textarea id="pickup-notes" rows="3" class="form-input" placeholder="Any special requests or instructions..."></textarea>

                <button type="submit" class="btn-primary" style="width: 100%; margin-top: 1.5rem;">
                    Confirm Order & Pay
                </button>
            </form>
        </div>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/cart.js' %}"></script>
{% endblock %}
```

**File**: `static/js/shop.js` (створити)
```javascript
// Shop functionality
class Shop {
    constructor() {
        this.products = [];
        this.cart = JSON.parse(localStorage.getItem('cart')) || [];
        this.init();
    }

    async init() {
        await this.loadProducts();
        this.setupFilters();
        this.updateCartBadge();
    }

    async loadProducts(category = 'all') {
        try {
            let url = '/api/shop/products/';
            if (category !== 'all') {
                url += `?category=${category}`;
            }

            const response = await fetch(url);
            this.products = await response.json();
            this.renderProducts();
        } catch (error) {
            console.error('Failed to load products:', error);
        }
    }

    renderProducts() {
        const grid = document.querySelector('.products-grid');
        if (!grid) return;

        grid.innerHTML = this.products.map(product => `
            <div class="product-card" data-category="${product.category}">
                <img src="${product.main_image}" alt="${product.name}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;">
                <h3 style="margin-top: 1rem;">${product.name}</h3>
                <p class="body-small" style="color: rgba(255,255,255,0.7);">${product.short_description}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <div>
                        <span style="text-decoration: line-through; color: rgba(255,255,255,0.5);">$${product.price}</span>
                        <span style="color: #B8860B; font-size: 1.25rem; font-weight: bold; margin-left: 0.5rem;">$${product.member_price}</span>
                    </div>
                    ${product.in_stock 
                        ? `<button class="btn-primary btn-small" onclick="shop.addToCart(${product.id}, '${product.name}', ${product.member_price}, '${product.main_image}')">Add to Cart</button>`
                        : `<span style="color: #EF4444;">Out of Stock</span>`
                    }
                </div>
            </div>
        `).join('');
    }

    setupFilters() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.loadProducts(e.target.dataset.category);
            });
        });
    }

    addToCart(id, name, price, image) {
        const existing = this.cart.find(item => item.id === id);
        if (existing) {
            existing.quantity++;
        } else {
            this.cart.push({ id, name, price, image, quantity: 1 });
        }
        localStorage.setItem('cart', JSON.stringify(this.cart));
        this.updateCartBadge();
        this.showNotification(`${name} added to pickup list!`);
    }

    updateCartBadge() {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
            badge.textContent = totalItems;
            badge.style.display = totalItems > 0 ? 'block' : 'none';
        }
    }

    showNotification(message) {
        // Simple notification (можна покращити)
        alert(message);
    }
}

// Initialize
const shop = new Shop();
```

##### **Day 5: Concierge Page**

**File**: `templates/concierge/request.html`
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Personal Concierge Service - CoreSync{% endblock %}

{% block content %}
<!-- Hero Section -->
<section class="hero-section" style="padding: 8rem 0 4rem;">
    <div class="container">
        <h1 class="heading-xlarge">Personal Concierge</h1>
        <p class="body-large" style="max-width: 600px; margin: 2rem auto;">
            Special requests for premium members. We'll source and prepare anything for your next visit.
        </p>
    </div>
</section>

<!-- Request Form -->
<section class="section">
    <div class="container" style="max-width: 800px;">
        <form id="concierge-form" class="contact-form">
            <div class="form-group">
                <label class="form-label">Request Type</label>
                <select id="request_type" class="form-input" required>
                    <option value="">Select type...</option>
                    <option value="alcohol">Premium Alcohol 🥃</option>
                    <option value="flowers">Fresh Flowers 🌹</option>
                    <option value="food">Gourmet Food 🍽️</option>
                    <option value="jewelry">Jewelry & Accessories 💎</option>
                    <option value="luxury">Luxury Items ✨</option>
                    <option value="gift">Gift Items 🎁</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Title</label>
                <input type="text" id="title" class="form-input" placeholder="Brief description..." required>
            </div>

            <div class="form-group">
                <label class="form-label">Detailed Description</label>
                <textarea id="description" class="form-textarea" rows="5" placeholder="Tell us exactly what you're looking for..." required></textarea>
            </div>

            <div class="form-group">
                <label class="form-label">Product Link (optional)</label>
                <input type="url" id="product_link" class="form-input" placeholder="https://...">
            </div>

            <div class="form-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div class="form-group">
                    <label class="form-label">Budget Minimum</label>
                    <input type="number" id="budget_min" class="form-input" placeholder="$0" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Budget Maximum</label>
                    <input type="number" id="budget_max" class="form-input" placeholder="$0" min="0" step="0.01" required>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Preferred Pickup Date</label>
                <input type="date" id="pickup_date" class="form-input" required>
            </div>

            <div class="form-notice" style="background: rgba(184,134,11,0.1); padding: 1.5rem; border-radius: 8px; margin: 2rem 0;">
                <p style="font-weight: bold; margin-bottom: 0.5rem;">📌 Important Notes:</p>
                <ul style="padding-left: 1.5rem;">
                    <li>Available for Premium & Unlimited members only</li>
                    <li>We'll review and approve within 24 hours</li>
                    <li>Items will be ready on your selected pickup date</li>
                    <li>Age verification required for alcohol purchases</li>
                </ul>
            </div>

            <button type="submit" class="btn-primary" style="width: 100%;">
                Submit Request
            </button>
        </form>

        <!-- My Requests -->
        <div id="my-requests" style="margin-top: 4rem;">
            <h2>My Requests</h2>
            <div id="requests-list">
                <!-- Loaded via JavaScript -->
            </div>
        </div>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/concierge.js' %}"></script>
{% endblock %}
```

**File**: `static/js/concierge.js` (створити)
```javascript
// Concierge functionality
class Concierge {
    constructor() {
        this.apiUrl = '/api/concierge/requests/';
        this.init();
    }

    async init() {
        this.setupForm();
        await this.loadMyRequests();
        this.setMinPickupDate();
    }

    setupForm() {
        const form = document.getElementById('concierge-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitRequest();
        });
    }

    setMinPickupDate() {
        const dateInput = document.getElementById('pickup_date');
        if (dateInput) {
            // Minimum 3 days from now
            const minDate = new Date();
            minDate.setDate(minDate.getDate() + 3);
            dateInput.min = minDate.toISOString().split('T')[0];
        }
    }

    async submitRequest() {
        const formData = {
            request_type: document.getElementById('request_type').value,
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            product_link: document.getElementById('product_link').value,
            budget_min: parseFloat(document.getElementById('budget_min').value),
            budget_max: parseFloat(document.getElementById('budget_max').value),
            preferred_pickup_date: document.getElementById('pickup_date').value,
        };

        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`,
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                alert('Request submitted successfully! We'll review it within 24 hours.');
                document.getElementById('concierge-form').reset();
                await this.loadMyRequests();
            } else {
                alert('Error submitting request. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        }
    }

    async loadMyRequests() {
        try {
            const response = await fetch(this.apiUrl, {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`,
                },
            });

            const requests = await response.json();
            this.renderRequests(requests);
        } catch (error) {
            console.error('Error loading requests:', error);
        }
    }

    renderRequests(requests) {
        const container = document.getElementById('requests-list');
        if (!container) return;

        if (requests.length === 0) {
            container.innerHTML = '<p style="color: rgba(255,255,255,0.5);">No requests yet.</p>';
            return;
        }

        container.innerHTML = requests.map(req => `
            <div class="request-card" style="background: rgba(255,255,255,0.05); padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3>${req.title}</h3>
                        <p style="color: rgba(255,255,255,0.7);">${req.request_type_display}</p>
                        <p style="margin-top: 0.5rem;">Budget: $${req.budget_min} - $${req.budget_max}</p>
                        <p>Pickup Date: ${new Date(req.preferred_pickup_date).toLocaleDateString()}</p>
                    </div>
                    <div>
                        <span class="status-badge status-${req.status}">${req.status_display}</span>
                        ${req.can_cancel ? `<button onclick="concierge.cancelRequest('${req.id}')" class="btn-secondary btn-small" style="margin-top: 0.5rem;">Cancel</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async cancelRequest(id) {
        if (!confirm('Are you sure you want to cancel this request?')) return;

        try {
            const response = await fetch(`${this.apiUrl}${id}/cancel_request/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`,
                },
            });

            if (response.ok) {
                alert('Request cancelled successfully.');
                await this.loadMyRequests();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    getToken() {
        // Implement token retrieval (from localStorage or cookie)
        return localStorage.getItem('access_token') || '';
    }
}

// Initialize
const concierge = new Concierge();
```

##### **Day 6-7: Legal Pages + Membership Detail**

(Продовжу в наступній частині через обмеження розміру...)

**Це перша частина покращеного плану. Продовжити?**

---

## 🎯 КЛЮЧОВІ ВІДМІННОСТІ ВІД ПОПЕРЕДНЬОГО ПЛАНУ

1. **Реальний код замість абстракцій** - всі моделі повністю написані
2. **Використання наявної архітектури** - базуюся на існуючих models/views
3. **QuickBooks integration** - вже вбудована в кожну модель
4. **Professional serializers** - з всіма полями та методами
5. **Детальні ViewSets** - з permissions, filters, custom actions
6. **JavaScript з API integration** - реальна взаємодія з backend
7. **Responsive HTML templates** - використовую наявні стилі
8. **Admin panels** - для staff management

**Хочете, щоб я продовжив з рештою плану?** ✨

