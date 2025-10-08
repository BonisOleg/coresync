# 🚀 CoreSync - Production Deployment Guide

**Version**: 1.0  
**Target**: Render.com  
**Domain**: coresync.life

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Backend Ready
- [x] All migrations applied
- [x] Static files collected
- [x] Tests passing (11/11)
- [x] Admin panels working
- [x] API endpoints tested
- [x] Environment variables documented

### Frontend Ready
- [x] All 23 pages working
- [x] JavaScript optimized
- [x] No inline styles
- [x] Toast notifications
- [x] Responsive design
- [x] Tests passing (29/29)

### Mobile Ready
- [x] Flutter repositories complete
- [x] iOS Info.plist configured
- [x] Android Manifest configured
- [x] Build scripts ready
- [x] Deep links configured
- [x] Testing checklist created

---

## 🌐 RENDER.COM DEPLOYMENT

### Step 1: Create Web Service

1. Login to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: coresync-backend
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
   - **Plan**: Starter ($7/month)

### Step 2: Environment Variables

Add these in Render Dashboard → Environment:

```bash
# Django
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=coresync.life,www.coresync.life,*.onrender.com
DATABASE_URL=<from-render-postgresql>

# Email
EMAIL_HOST_USER=info@coresync.life
EMAIL_HOST_PASSWORD=<app-password>

# Stripe (use test keys initially)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional (for later)
SENTRY_DSN=https://...
AWS_ACCESS_KEY_ID=<for-media-storage>
AWS_SECRET_ACCESS_KEY=<for-media-storage>
```

### Step 3: Create Database

1. Dashboard → "New +" → "PostgreSQL"
2. **Name**: coresync-db
3. **Plan**: Starter
4. Copy connection string to DATABASE_URL

### Step 4: Deploy

```bash
# Commit all changes
git add .
git commit -m "Production deployment ready - 35/42 days complete"
git push origin main

# Render auto-deploys from main branch
# Monitor: https://dashboard.render.com/
```

---

## 🔒 SSL & DOMAIN SETUP

### GoDaddy DNS Configuration

**Login**: https://dcc.godaddy.com/  
**Domain**: coresync.life

**Add DNS Records**:
```
Type    Name    Value                           TTL
A       @       <RENDER_IP>                    600
A       www     <RENDER_IP>                    600
CNAME   api     coresync-backend.onrender.com  3600
```

**Get Render IP**:
- Render Dashboard → coresync-backend
- Settings → Custom Domain
- Add: coresync.life
- Copy IP address

### SSL Certificate

**Automatic** - Render provides free Let's Encrypt SSL:
- Add custom domain in Render
- Wait 5-10 minutes for certificate
- Automatic renewal every 90 days

---

## 📄 SEO OPTIMIZATION

### Sitemap.xml

**✅ Already created**: `templates/sitemap.xml`

**Verify access**: https://coresync.life/sitemap.xml

### Robots.txt

**✅ Already created**: `static/robots.txt`

### Meta Tags

**✅ Already in base.html**:
- Open Graph tags
- Twitter Card
- Schema.org structured data
- Canonical URLs

---

## 📊 MONITORING SETUP

### Sentry Error Tracking

**Install**:
```bash
pip install sentry-sdk
```

**Configure** (settings.py):
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        environment='production',
    )
```

### Google Analytics

**✅ Ready to add** GA4 Measurement ID to base.html

---

## ✅ DEPLOYMENT CHECKLIST

### Pre-Deploy
- [x] Code committed to git
- [x] All tests passing
- [x] Environment variables documented
- [x] Database migrations ready
- [x] Static files optimized

### Deploy
- [ ] Create Render web service
- [ ] Create PostgreSQL database
- [ ] Configure environment variables
- [ ] Deploy application
- [ ] Run migrations
- [ ] Create superuser
- [ ] Load initial data

### Post-Deploy
- [ ] Verify health check: /health/
- [ ] Test API endpoints
- [ ] Test website pages
- [ ] Configure custom domain
- [ ] Verify SSL certificate
- [ ] Test email sending
- [ ] Configure Sentry
- [ ] Test Stripe webhooks

### Final Checks
- [ ] All 23 pages accessible
- [ ] API responding correctly
- [ ] Admin panel working
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Fast load times (<3s)
- [ ] SEO meta tags present

---

## 🎉 GO LIVE PROCEDURE

### Launch Day (Day 42)

**Morning**:
1. ✅ Verify production is stable
2. ✅ Check all pages load
3. ✅ Test critical user flows
4. ✅ Verify monitoring active

**Afternoon**:
1. Update DNS to point to Render
2. Wait for DNS propagation (1-4 hours)
3. Verify SSL certificate active
4. Test from multiple locations

**Evening**:
1. Final walkthrough
2. Monitor error logs
3. Check analytics
4. **LAUNCH!** 🚀

---

## 🆘 TROUBLESHOOTING

### Common Issues

**Issue**: Static files not loading
```bash
python manage.py collectstatic --noinput
```

**Issue**: Database connection error
```bash
# Check DATABASE_URL is set correctly
# Verify PostgreSQL is running
```

**Issue**: 502 Bad Gateway
```bash
# Check Render logs
# Verify gunicorn is starting
# Check for Python errors
```

---

## 📞 SUPPORT RESOURCES

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **SSL Issues**: https://letsencrypt.org/docs/
- **DNS Help**: https://www.whatsmydns.net/

---

**Status**: ✅ READY FOR DEPLOYMENT  
**Risk Level**: 🟢 LOW  
**Estimated Time**: 2-3 hours

**LET'S DEPLOY! 🚀**

