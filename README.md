# CoreSync - Premium Wellness Experience Platform

## 🏆 Project Overview

CoreSync is a cutting-edge wellness platform that combines AI-powered technology with luxury spa services. The platform offers personalized wellness experiences through advanced massage beds, meditation pods, and IoT-controlled environments.

## 🚀 Key Features

### Backend (Django)
- **RESTful API** with Django REST Framework
- **User Management** with authentication & profiles
- **Membership System** with tiered pricing
- **Service Management** for spa treatments
- **IoT Control** for smart devices
- **Payment Processing** integration
- **Analytics** and reporting

### Frontend (Django Templates)
- **Responsive Design** for all devices
- **Mobile-First** approach with iOS Safari optimization
- **Interactive Galleries** with touch/swipe support
- **AI Assistant Widget** with WhatsApp fallback
- **Membership Portal** with comparison tables
- **Booking System** with calendar integration

### Mobile App (Flutter)
- **Cross-platform** iOS & Android support
- **Face Recognition** for secure login
- **IoT Device Control** for spa equipment
- **Personalized Recommendations** powered by AI
- **Real-time Booking** and scheduling

## 🛠 Technology Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database (development)
- **Celery** - Task queue (planned)
- **Redis** - Caching (planned)

### Frontend
- **HTML5/CSS3** - Markup and styling
- **JavaScript (ES6+)** - Interactive features
- **Responsive Design** - Mobile-first approach
- **Touch Gestures** - Mobile optimization

### Mobile
- **Flutter** - Cross-platform development
- **Dart** - Programming language
- **Custom UI Components** - Brand-specific design

## 📁 Project Structure

```
SPA-AI/
├── coresync_backend/          # Django backend
│   ├── config/               # Django settings
│   ├── users/                # User management
│   ├── memberships/          # Membership system
│   ├── services/             # Service management
│   ├── payments/             # Payment processing
│   ├── iot_control/          # IoT device control
│   ├── analytics/            # Analytics & reporting
│   ├── static/               # Static files (CSS, JS, images)
│   └── templates/            # Django templates
├── coresync_mobile/          # Flutter mobile app
│   ├── lib/                  # Dart source code
│   ├── assets/               # App assets
│   └── android/ios/          # Platform-specific code
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Backend Setup
```bash
# Navigate to backend
cd coresync_backend

# Activate virtual environment
source ../coresync_env/bin/activate

# Install dependencies
pip install -r requirements/backend_requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Mobile App Setup
```bash
# Navigate to mobile app
cd coresync_mobile

# Install Flutter dependencies
flutter pub get

# Run on device/emulator
flutter run
```

## 🎨 Design System

### Brand Colors
- **Primary Gold**: #B8860B
- **Background**: #000000
- **Text**: #FFFFFF
- **Accent**: rgba(255, 255, 255, 0.1)

### Typography
- **Headings**: Maison Neue Bold
- **Body**: Maison Neue Book
- **Monospace**: Maison Neue Mono

## 📱 Responsive Breakpoints

- **Desktop**: 1200px+
- **Tablet**: 768px - 1024px
- **Mobile**: < 768px
- **iOS Safari**: Special optimizations

## 🔧 Recent Updates

### v1.2.0 - Image Optimization & Gallery Fix
- ✅ Optimized image file sizes (95% reduction)
- ✅ Fixed gallery cropping issues
- ✅ Added responsive carousel functionality
- ✅ Improved mobile touch gestures
- ✅ Enhanced iOS Safari compatibility

### v1.1.0 - Membership System
- ✅ Implemented tiered membership plans
- ✅ Added comparison tables
- ✅ Created booking system
- ✅ Integrated AI assistant widget

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Contact

- **Email**: info@coresync.life
- **Phone**: 551.574.2281
- **Address**: 1544 71st Street, Brooklyn, NY 11228

---

**Built with ❤️ for premium wellness experiences**