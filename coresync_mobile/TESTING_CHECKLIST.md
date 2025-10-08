# 📱 CoreSync Mobile App - Testing Checklist

## Pre-Release Testing

### ✅ Authentication
- [ ] Email/Password login works
- [ ] Face registration (3 captures minimum)
- [ ] Face authentication (matches registered face)
- [ ] Face authentication (rejects unknown faces)
- [ ] Logout clears all data
- [ ] Token refresh works
- [ ] Biometric fallback to password

### ✅ Booking Flow
- [ ] View available services
- [ ] Filter by category (Mensuite/Private)
- [ ] Select date (calendar works)
- [ ] View available time slots
- [ ] Member sees priority slots
- [ ] Non-member sees limited slots (3 days)
- [ ] Select add-ons
- [ ] Confirm booking
- [ ] Receive confirmation
- [ ] View upcoming bookings
- [ ] Cancel booking (within allowed time)
- [ ] Reschedule booking

### ✅ IoT Control
- [ ] Connect to room devices
- [ ] Control lighting (brightness 0-100%)
- [ ] Control lighting (5 color presets)
- [ ] Control temperature (65-80°F)
- [ ] Start meditation session
- [ ] Start massage program
- [ ] Set immersive scene
- [ ] Save custom scene
- [ ] WebSocket real-time updates

### ✅ Shop
- [ ] Browse products (11+ products)
- [ ] Filter by category (4 categories)
- [ ] Add to cart
- [ ] View cart
- [ ] Update quantity
- [ ] Remove from cart
- [ ] Checkout
- [ ] View order status
- [ ] Cancel order

### ✅ Concierge
- [ ] Submit request (7 types)
- [ ] View request history
- [ ] Cancel pending request
- [ ] Receive status updates
- [ ] Budget validation works

### ✅ Push Notifications
- [ ] Receive notification (app in foreground)
- [ ] Receive notification (app in background)
- [ ] Notification opens correct screen
- [ ] Badge count updates

### ✅ Performance
- [ ] Cold start < 3 seconds
- [ ] No frame drops (60 FPS)
- [ ] Memory usage < 200 MB
- [ ] Network requests optimized
- [ ] Images load smoothly
- [ ] No crashes during 30min session

### ✅ Devices Tested
- [ ] iPhone 12 (iOS 16)
- [ ] iPhone 14 Pro (iOS 17)
- [ ] Pixel 6 (Android 13)
- [ ] Samsung Galaxy S22 (Android 14)

### ✅ Build & Distribution
- [ ] iOS builds without errors
- [ ] Android builds without errors
- [ ] App size < 50 MB
- [ ] No security warnings
- [ ] All permissions justified

---

## Test Results Log

**Date**: ___________

**Tester**: ___________

**Build**: ___________

**Results**: _____ / _____ tests passed

**Issues Found**:
1. 
2. 
3. 

**Status**: [ ] Ready for submission  [ ] Needs fixes

---

## Sign-off

- [ ] All critical features tested
- [ ] No blocking bugs
- [ ] Performance acceptable
- [ ] Ready for App Store submission

**Approved by**: ___________  
**Date**: ___________

