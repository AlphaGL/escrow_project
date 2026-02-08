# TrustEscrow Nigeria - Secure Escrow Payment Platform

A complete Django-based escrow payment platform with Paystack integration, built specifically for the Nigerian market to solve trust issues in service payments.

## 🎯 Problem & Solution

**Problem:**
- Clients lose money to fraudulent service providers
- Service providers don't get paid after completing work
- Lack of trust in online service transactions

**Solution:**
TrustEscrow holds payments securely until work is completed and approved, protecting both parties.

## ✨ Key Features

### Core Functionality
- ✅ **Escrow System**: Secure fund holding until work completion
- ✅ **Auto-Release**: Automatic payment release after deadline
- ✅ **Dispute Resolution**: Admin-managed dispute handling
- ✅ **User Wallets**: Balance tracking and management
- ✅ **Transaction Timeline**: Complete audit trail
- ✅ **Messaging System**: In-transaction communication

### Payment Features
- ✅ **Paystack Integration**: Card, bank transfer, USSD payments
- ✅ **Multiple Payment Methods**: Flexible payment options
- ✅ **Webhook Support**: Real-time payment notifications
- ✅ **Transaction Verification**: Secure payment confirmation

### User Features
- ✅ **Dual User Types**: Clients, Service Providers, or Both
- ✅ **Trust Scores**: Reputation system
- ✅ **Ratings & Reviews**: Post-transaction feedback
- ✅ **Profile Management**: Complete user profiles
- ✅ **Bank Details**: Secure withdrawal information

### Admin Features
- ✅ **Comprehensive Dashboard**: Full platform oversight
- ✅ **Dispute Management**: Resolution tools
- ✅ **User Management**: Complete user control
- ✅ **Transaction Monitoring**: Real-time oversight

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (or use SQLite for development)
- Redis (for Celery tasks)
- Paystack Account

### Installation

1. **Clone and Setup**
```bash
cd escrow_platform
cp .env.example .env
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
Edit `.env` file with your settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Paystack Keys (Get from https://dashboard.paystack.com/#/settings/developer)
PAYSTACK_SECRET_KEY=sk_test_your_key_here
PAYSTACK_PUBLIC_KEY=pk_test_your_key_here

# Database (SQLite for development, PostgreSQL for production)
# For development, these are optional
DB_NAME=escrow_db
DB_USER=postgres
DB_PASSWORD=your_password

# Email (for notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Visit: http://localhost:8000

### Running Celery (for Auto-Release)

In a separate terminal:
```bash
# Start Redis first
redis-server

# In another terminal
celery -A config worker -l info

# In another terminal (for periodic tasks)
celery -A config beat -l info
```

## 📁 Project Structure

```
escrow_platform/
├── config/                 # Django settings and configuration
│   ├── settings.py        # Main settings
│   ├── urls.py           # URL routing
│   ├── celery.py         # Celery configuration
│   └── wsgi.py           # WSGI application
├── accounts/              # User management app
│   ├── models.py         # User, Wallet, Rating models
│   ├── views.py          # Authentication and profile views
│   ├── forms.py          # Registration and profile forms
│   └── admin.py          # Admin configuration
├── transactions/          # Escrow transaction app
│   ├── models.py         # Transaction, Message, Timeline models
│   ├── views.py          # Transaction management views
│   ├── tasks.py          # Celery tasks (auto-release)
│   ├── forms.py          # Transaction and dispute forms
│   └── admin.py          # Admin configuration
├── payments/              # Payment processing app
│   ├── models.py         # Payment and Payout models
│   ├── views.py          # Payment views
│   ├── paystack.py       # Paystack API integration
│   └── admin.py          # Admin configuration
├── core/                  # Core app (homepage, dashboard)
│   ├── models.py         # Site settings, FAQ, Testimonials
│   ├── views.py          # Core views
│   └── admin.py          # Admin configuration
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── core/             # Core templates
│   ├── accounts/         # Account templates
│   ├── transactions/     # Transaction templates
│   └── payments/         # Payment templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── images/           # Images
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```

## 🔑 Key Workflows

### 1. Creating a Transaction (Client)
1. Client logs in
2. Clicks "New Transaction"
3. Enters service provider details (email/phone)
4. Specifies amount and service description
5. Proceeds to payment
6. Pays via Paystack
7. Money held in escrow

### 2. Completing Work (Service Provider)
1. Provider receives notification
2. Accepts and starts work
3. Completes the service
4. Marks work as completed
5. Waits for client approval

### 3. Payment Release (Client)
1. Client receives completion notification
2. Reviews the work
3. Options:
   - Approve → Money released immediately
   - Dispute → Money frozen, admin resolves
   - Do nothing → Auto-release after 5 days

### 4. Dispute Resolution (Admin)
1. Admin reviews evidence from both parties
2. Decides resolution:
   - Full refund to client (100%)
   - Full payment to provider (0%)
   - Partial refund (custom percentage)
3. Money distributed accordingly

## 💳 Paystack Integration

### Getting Started with Paystack

1. **Create Account**: https://dashboard.paystack.com/signup
2. **Get API Keys**: Dashboard → Settings → API Keys & Webhooks
3. **Test Mode**: Use test keys (sk_test_xxx and pk_test_xxx)
4. **Live Mode**: Switch to live keys when ready

### Webhook Setup

1. Go to: Dashboard → Settings → API Keys & Webhooks
2. Add webhook URL: `https://yourdomain.com/payments/webhook/`
3. Events to listen for: `charge.success`

### Supported Payment Methods
- Debit/Credit Cards (Visa, Mastercard, Verve)
- Bank Transfer
- USSD
- Mobile Money

## 🎨 Design Philosophy

The platform uses a trust-building design with:

### Color Scheme
- **Primary Blue (#0066CC)**: Trust, security, professionalism
- **Secondary Green (#00A86B)**: Growth, money, success
- **Accent Orange (#FFA500)**: Energy, call-to-action

### Trust Elements
- 🛡️ Security badges and icons
- 🔒 Lock symbols throughout
- ✅ Checkmarks for completed steps
- 📊 Transparent transaction timelines
- ⭐ User ratings and reviews
- 💬 Clear communication channels

### User Experience
- Clean, professional interface
- Mobile-responsive design
- Clear status indicators
- Step-by-step workflows
- Instant notifications

## 🔒 Security Features

- ✅ HTTPS/SSL encryption (production)
- ✅ CSRF protection
- ✅ Secure password hashing
- ✅ Rate limiting (Paystack)
- ✅ Transaction audit logs
- ✅ Admin-only dispute resolution
- ✅ Webhook signature verification
- ✅ Two-factor authentication ready

## 📊 Admin Panel

Access: http://localhost:8000/admin

Features:
- User management
- Transaction monitoring
- Dispute resolution
- Payment tracking
- Platform statistics
- Content management (FAQs, testimonials)

## 🚀 Deployment (Production)

### Using Heroku

1. **Install Heroku CLI**
2. **Create Heroku App**
```bash
heroku create trustescrow-ng
```

3. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. **Add Redis**
```bash
heroku addons:create heroku-redis:hobby-dev
```

5. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=your-production-key
heroku config:set DEBUG=False
heroku config:set PAYSTACK_SECRET_KEY=sk_live_xxx
heroku config:set PAYSTACK_PUBLIC_KEY=pk_live_xxx
```

6. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Using DigitalOcean/AWS

1. **Setup Server** (Ubuntu 20.04+)
2. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql redis-server
```

3. **Setup Application**
```bash
git clone your-repo
cd escrow_platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

4. **Configure Nginx**
5. **Setup Supervisor** (for Gunicorn and Celery)
6. **Configure SSL** (Let's Encrypt)

## 📱 API Documentation

The platform includes a REST API for future mobile app integration.

Endpoints:
- `/api/transactions/` - Transaction management
- `/api/payments/` - Payment processing
- `/api/users/` - User information

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

Test Paystack integration:
```python
# Use test cards from Paystack docs
# Success: 4084084084084081
# Declined: 5060666666666666666
```

## 📈 Future Enhancements

- [ ] Mobile apps (iOS/Android)
- [ ] SMS notifications
- [ ] KYC/BVN verification
- [ ] Multi-currency support
- [ ] Installment payments
- [ ] Automated refunds
- [ ] Advanced analytics dashboard
- [ ] AI-powered fraud detection

## 🤝 Support

For issues or questions:
- Email: support@trustescrow.ng
- GitHub Issues: [Create an issue]

## 📄 License

This project is proprietary. All rights reserved.

## 👥 Team

Built for solving trust issues in Nigerian service payments.

---

**Remember**: Always use test API keys during development. Switch to live keys only when ready for production!
