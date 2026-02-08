# TrustEscrow Nigeria - Customization & Extension Guide

## 🎨 Customization Guide

### Changing Colors and Branding

**1. Update Colors in CSS**

Edit `static/css/main.css`:

```css
:root {
    /* Change these to your brand colors */
    --primary-color: #0066CC;      /* Your main brand color */
    --secondary-color: #00A86B;    /* Your accent color */
    --accent-color: #FFA500;       /* Call-to-action color */
}
```

**2. Add Your Logo**

```python
# In admin panel:
# 1. Go to Site Settings
# 2. Upload your logo
# 3. Update site name and description
```

**3. Customize Email Templates**

Create `templates/emails/transaction_created.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #0066CC; color: white; padding: 20px; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TrustEscrow Nigeria</h1>
    </div>
    <div class="content">
        <h2>New Transaction Created</h2>
        <p>Dear {{ user.get_full_name }},</p>
        <p>Your transaction {{ transaction.reference }} has been created.</p>
        <!-- Add more details -->
    </div>
</body>
</html>
```

### Platform Settings

**Transaction Limits**

Edit `config/settings.py`:

```python
# Adjust these values
MIN_TRANSACTION_AMOUNT = 1000      # ₦1,000
MAX_TRANSACTION_AMOUNT = 500000    # ₦500,000
PLATFORM_FEE_PERCENTAGE = 2.5      # 2.5%
AUTO_RELEASE_DAYS = 5              # 5 days
```

**Auto-Release Timing**

Change the auto-release check frequency in `config/celery.py`:

```python
app.conf.beat_schedule = {
    'check-auto-release-transactions': {
        'task': 'transactions.tasks.check_auto_release',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        # Change to: crontab(hour='*/1')  # Every hour
        # Or: crontab(minute='0', hour='9,17')  # 9am and 5pm
    },
}
```

## 🔧 Adding New Features

### Feature 1: Transaction Categories

**1. Update Transaction Model**

Edit `transactions/models.py`:

```python
class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('WEB', 'Web Development'),
        ('DESIGN', 'Graphic Design'),
        ('WRITING', 'Content Writing'),
        ('MARKETING', 'Digital Marketing'),
        ('PLUMBING', 'Plumbing Services'),
        ('ELECTRICAL', 'Electrical Work'),
        ('OTHER', 'Other'),
    ]
    
    service_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER'
    )
```

**2. Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### Feature 2: SMS Notifications

**1. Install Africa's Talking**

```bash
pip install africastalking
```

**2. Create SMS Service**

Create `core/sms.py`:

```python
import africastalking
from django.conf import settings

africastalking.initialize(
    settings.AT_USERNAME,
    settings.AT_API_KEY
)

sms = africastalking.SMS

def send_sms(phone_number, message):
    """Send SMS notification"""
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"SMS Error: {e}")
        return None
```

**3. Add to Settings**

```python
# config/settings.py
AT_USERNAME = config('AT_USERNAME', default='sandbox')
AT_API_KEY = config('AT_API_KEY', default='')
```

**4. Use in Views**

```python
from core.sms import send_sms

# In transaction creation
send_sms(
    provider.phone_number,
    f"New job from {client.get_full_name()}. Amount: ₦{amount}"
)
```

### Feature 3: Transaction Milestones

**1. Create Milestone Model**

Add to `transactions/models.py`:

```python
class TransactionMilestone(models.Model):
    """Break transaction into milestones"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
```

**2. Update Transaction Logic**

```python
def complete_milestone(milestone_id):
    milestone = TransactionMilestone.objects.get(id=milestone_id)
    milestone.is_completed = True
    milestone.completed_at = timezone.now()
    milestone.save()
    
    # Check if all milestones are complete
    transaction = milestone.transaction
    if transaction.milestones.filter(is_completed=False).count() == 0:
        transaction.complete_work()
```

### Feature 4: Subscription Plans

**1. Create Subscription Model**

Create `accounts/subscriptions.py`:

```python
from django.db import models

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_transactions_per_month = models.IntegerField()
    reduced_fee_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )
    
    def __str__(self):
        return f"{self.get_name_display()} - ₦{self.price}/month"

class UserSubscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
```

### Feature 5: Referral System

**1. Add to User Model**

```python
class User(AbstractUser):
    # ... existing fields ...
    
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    referral_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
```

**2. Add Referral Bonus Logic**

```python
# In transaction completion
if transaction.service_provider.referred_by:
    referrer = transaction.service_provider.referred_by
    bonus = transaction.service_provider_amount * Decimal('0.05')  # 5% bonus
    referrer.wallet.balance += bonus
    referrer.referral_earnings += bonus
    referrer.wallet.save()
    referrer.save()
```

## 📊 Analytics & Reporting

### Add Transaction Analytics

Create `core/analytics.py`:

```python
from django.db.models import Sum, Count, Avg
from transactions.models import Transaction
from datetime import datetime, timedelta

def get_platform_stats():
    """Get overall platform statistics"""
    today = datetime.now().date()
    last_30_days = today - timedelta(days=30)
    
    stats = {
        'total_transactions': Transaction.objects.count(),
        'total_volume': Transaction.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'monthly_transactions': Transaction.objects.filter(
            created_at__gte=last_30_days
        ).count(),
        'success_rate': calculate_success_rate(),
        'average_transaction': Transaction.objects.aggregate(
            avg=Avg('amount')
        )['avg'] or 0,
    }
    
    return stats

def calculate_success_rate():
    """Calculate percentage of successful transactions"""
    total = Transaction.objects.count()
    if total == 0:
        return 0
    
    successful = Transaction.objects.filter(
        status='RELEASED'
    ).count()
    
    return (successful / total) * 100
```

### Create Admin Dashboard View

Create `core/admin_dashboard.py`:

```python
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .analytics import get_platform_stats

@staff_member_required
def admin_dashboard_view(request):
    """Custom admin dashboard with analytics"""
    stats = get_platform_stats()
    
    # Recent disputes
    disputes = Transaction.objects.filter(
        is_disputed=True,
        dispute_resolved_at__isnull=True
    )
    
    context = {
        'stats': stats,
        'pending_disputes': disputes,
    }
    
    return render(request, 'admin/dashboard.html', context)
```

## 🔐 Security Enhancements

### Add Two-Factor Authentication

**1. Install django-otp**

```bash
pip install django-otp qrcode
```

**2. Add to Settings**

```python
INSTALLED_APPS = [
    # ... other apps
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    # ... other middleware
    'django_otp.middleware.OTPMiddleware',
]
```

**3. Create 2FA Setup View**

```python
from django_otp.plugins.otp_totp.models import TOTPDevice

def setup_2fa(request):
    if request.method == 'POST':
        device = TOTPDevice.objects.create(
            user=request.user,
            name='default'
        )
        # Generate QR code
        url = device.config_url
        return render(request, 'accounts/2fa_qr.html', {'url': url})
```

### Add Rate Limiting

**1. Install django-ratelimit**

```bash
pip install django-ratelimit
```

**2. Apply to Views**

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Your login logic
    pass
```

## 🌍 Internationalization

### Add Multi-Language Support

**1. Update Settings**

```python
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
    ('yo', 'Yoruba'),
    ('ig', 'Igbo'),
    ('ha', 'Hausa'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

**2. Mark Strings for Translation**

```python
from django.utils.translation import gettext_lazy as _

class Transaction(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', _('Pending')),
            ('PAID', _('Paid')),
            # ... other choices
        ]
    )
```

**3. Create Translation Files**

```bash
python manage.py makemessages -l yo
python manage.py makemessages -l ig
python manage.py compilemessages
```

## 📱 Mobile API

### Add REST API for Mobile Apps

**1. Create API Views**

Create `api/views.py`:

```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from transactions.models import Transaction
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(
            Q(client=self.request.user) |
            Q(service_provider=self.request.user)
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve transaction"""
        transaction = self.get_object()
        if transaction.client != request.user:
            return Response({'error': 'Unauthorized'}, status=403)
        
        transaction.approve_payment()
        return Response({'status': 'approved'})
```

**2. Create Serializers**

Create `api/serializers.py`:

```python
from rest_framework import serializers
from transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source='client.get_full_name',
        read_only=True
    )
    provider_name = serializers.CharField(
        source='service_provider.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'amount', 'status',
            'client_name', 'provider_name',
            'service_description', 'created_at'
        ]
        read_only_fields = ['reference', 'created_at']
```

## 🔄 Database Backups

### Automated Backups Script

Create `scripts/backup_db.py`:

```python
import os
from datetime import datetime
from django.core.management import call_command

def backup_database():
    """Create database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    filename = f'{backup_dir}/backup_{timestamp}.json'
    
    with open(filename, 'w') as f:
        call_command('dumpdata', stdout=f, indent=2)
    
    print(f'Backup created: {filename}')

if __name__ == '__main__':
    backup_database()
```

### Run Backup

```bash
python scripts/backup_db.py
```

## 📧 Email Templates

### Create Professional Email Templates

Create `templates/emails/base_email.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f8f9fa;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #0066CC, #004C99);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #00A86B;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .footer {
            background: #212529;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ TrustEscrow Nigeria</h1>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
        <div class="footer">
            <p>© 2024 TrustEscrow Nigeria. All rights reserved.</p>
            <p>Questions? Contact us at support@trustescrow.ng</p>
        </div>
    </div>
</body>
</html>
```

---

This guide covers the main customization options. The platform is designed to be easily extended with new features!
