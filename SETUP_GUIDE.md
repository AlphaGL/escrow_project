# TrustEscrow Nigeria - Complete Setup Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Paystack Configuration](#paystack-configuration)
4. [Running the Application](#running-the-application)
5. [Testing the Platform](#testing-the-platform)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 2GB RAM
- 10GB storage
- Modern web browser

### Recommended
- Python 3.11+
- 4GB RAM
- PostgreSQL database
- Redis server

## Initial Setup

### Step 1: Extract and Navigate
```bash
# Navigate to the project directory
cd escrow_platform
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter any errors, try:
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your actual values
# On Windows: notepad .env
# On macOS: open -e .env
# On Linux: nano .env
```

**Required .env Variables:**
```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-xyz123
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development - no need to change)
# The app will use SQLite automatically in DEBUG mode

# Paystack (MOST IMPORTANT!)
PAYSTACK_SECRET_KEY=sk_test_your_key_from_paystack_dashboard
PAYSTACK_PUBLIC_KEY=pk_test_your_key_from_paystack_dashboard

# Email (Optional for testing, but recommended)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Site Settings
SITE_NAME=TrustEscrow Nigeria
SITE_URL=http://localhost:8000
AUTO_RELEASE_DAYS=5
PLATFORM_FEE_PERCENTAGE=2.5
```

### Step 5: Initialize Database
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: accounts, admin, auth, contenttypes, core, payments, sessions, transactions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   ... (more migrations)
```

### Step 6: Create Admin User
```bash
python manage.py createsuperuser

# Enter:
# Email address: admin@trustescrow.ng
# Username: admin
# First name: Admin
# Last name: User
# Phone number: 08012345678
# Password: (choose a strong password)
# Password (again): (repeat password)
```

### Step 7: Load Initial Data (Optional)
```bash
# Create some sample data
python manage.py shell

# In the Python shell:
from core.models import FAQ, SiteSettings
from accounts.models import User

# Create site settings
settings = SiteSettings.objects.create(
    site_name='TrustEscrow Nigeria',
    support_email='support@trustescrow.ng',
    support_phone='+234 800 000 0000'
)

# Create some FAQs
FAQ.objects.create(
    question='How does escrow work?',
    answer='Escrow holds your payment safely until the service is completed and approved.',
    order=1
)

FAQ.objects.create(
    question='What are the fees?',
    answer='We charge a 2.5% platform fee on each transaction.',
    order=2
)

# Exit shell
exit()
```

## Paystack Configuration

### Getting Your API Keys

1. **Create Paystack Account**
   - Visit: https://dashboard.paystack.com/signup
   - Sign up with your email
   - Verify your email address

2. **Get Test API Keys**
   - Log in to Paystack Dashboard
   - Go to: Settings → API Keys & Webhooks
   - Copy your **Test Secret Key** (starts with `sk_test_`)
   - Copy your **Test Public Key** (starts with `pk_test_`)

3. **Add Keys to .env**
   ```env
   PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
   PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
   ```

### Test Cards for Development

Use these test cards from Paystack:

**Successful Payment:**
- Card Number: 4084 0840 8408 4081
- CVV: 408
- Expiry: Any future date
- PIN: 0000

**Declined Payment:**
- Card Number: 5060 6666 6666 6666 666
- CVV: 123
- Expiry: Any future date

## Running the Application

### Method 1: Simple Development Server

```bash
# Start the Django development server
python manage.py runserver

# You should see:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK (Windows) or CONTROL-C (Mac/Linux)
```

Visit: **http://localhost:8000**

### Method 2: With Celery (For Auto-Release Feature)

You need 3 terminal windows:

**Terminal 1: Django Server**
```bash
cd escrow_platform
venv\Scripts\activate  # On Windows
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
cd escrow_platform
venv\Scripts\activate  # On Windows
celery -A config worker -l info
```

**Terminal 3: Celery Beat (Periodic Tasks)**
```bash
cd escrow_platform
venv\Scripts\activate  # On Windows
celery -A config beat -l info
```

**Note:** Celery requires Redis. If you don't have Redis:
- Windows: Download from https://github.com/microsoftarchive/redis/releases
- macOS: `brew install redis` then `redis-server`
- Linux: `sudo apt install redis-server`

## Testing the Platform

### 1. Access Admin Panel
- URL: http://localhost:8000/admin
- Login with the superuser credentials you created
- Explore: Users, Transactions, Payments, FAQs, etc.

### 2. Create Test Users

```bash
python manage.py shell

from accounts.models import User

# Create a client
client = User.objects.create_user(
    email='client@test.com',
    username='testclient',
    password='testpass123',
    first_name='John',
    last_name='Client',
    phone_number='08011111111',
    user_type='CLIENT'
)

# Create a service provider
provider = User.objects.create_user(
    email='provider@test.com',
    username='testprovider',
    password='testpass123',
    first_name='Jane',
    last_name='Provider',
    phone_number='08022222222',
    user_type='PROVIDER'
)

exit()
```

### 3. Test Complete Transaction Flow

**A. As Client (Create Transaction)**
1. Logout from admin
2. Go to http://localhost:8000
3. Click "Login"
4. Email: `client@test.com`, Password: `testpass123`
5. Click "New Transaction"
6. Fill in:
   - Service Provider Email: `provider@test.com`
   - Amount: `10000`
   - Service Description: "Website design"
   - Service Category: "Web Development"
7. Click "Create Transaction"
8. Click "Pay Now"

**B. Make Payment (Paystack)**
1. You'll be redirected to Paystack
2. Use test card: `4084 0840 8408 4081`
3. Enter any future expiry date
4. CVV: `408`
5. PIN: `0000`
6. Complete payment

**C. As Provider (Complete Work)**
1. Logout
2. Login as provider: `provider@test.com` / `testpass123`
3. Go to "My Transactions"
4. Click on the transaction
5. Click "Start Work"
6. Click "Mark as Completed"

**D. As Client (Approve Payment)**
1. Logout
2. Login as client again
3. Go to "My Transactions"
4. Click on the transaction
5. Click "Approve Payment"
6. Money is released to provider!

### 4. Test Dispute Flow
1. Instead of approving, click "Raise Dispute"
2. Enter dispute reason
3. Login as admin at /admin
4. Go to Transactions → find the disputed transaction
5. Manually resolve the dispute

## Production Deployment

### Heroku Deployment

1. **Install Heroku CLI**
   - Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Login and Create App**
   ```bash
   heroku login
   heroku create trustescrow-ng
   ```

3. **Add PostgreSQL and Redis**
   ```bash
   heroku addons:create heroku-postgresql:mini
   heroku addons:create heroku-redis:mini
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-production-secret-key"
   heroku config:set DEBUG=False
   heroku config:set PAYSTACK_SECRET_KEY="sk_live_your_key"
   heroku config:set PAYSTACK_PUBLIC_KEY="pk_live_your_key"
   ```

5. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

6. **Run Migrations**
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

7. **Scale Workers**
   ```bash
   heroku ps:scale web=1 worker=1 beat=1
   ```

## Troubleshooting

### Common Issues

**1. "No module named 'django'"**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

**2. "Invalid API Key" from Paystack**
- Check your .env file
- Make sure keys start with `sk_test_` and `pk_test_`
- No spaces before or after the keys

**3. "Port already in use"**
```bash
# Use a different port
python manage.py runserver 8080
```

**4. Database errors**
```bash
# Delete database and start fresh
del db.sqlite3  # Windows
rm db.sqlite3   # Mac/Linux

# Recreate
python manage.py migrate
python manage.py createsuperuser
```

**5. Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**6. Celery not working on Windows**
- Windows doesn't fully support Celery
- For testing, the app works fine without Celery
- Auto-release just won't happen automatically
- You can manually release payments from admin panel

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Search the error on Google/Stack Overflow
3. Check Django logs in console
4. Verify all environment variables are set correctly
5. Make sure virtual environment is activated

## Next Steps

After successful setup:
1. ✅ Customize the design in `static/css/main.css`
2. ✅ Add your logo to `static/images/`
3. ✅ Update site settings in admin panel
4. ✅ Add FAQs and testimonials
5. ✅ Test thoroughly before going live
6. ✅ Switch to live Paystack keys for production
7. ✅ Set up proper email service (SendGrid, etc.)
8. ✅ Configure custom domain
9. ✅ Enable HTTPS/SSL

## Important Notes

- **Never commit .env file** - it contains secrets!
- **Use test keys** during development
- **Test all flows** before going live
- **Backup database** regularly in production
- **Monitor transactions** closely when live

---

**You're all set!** 🚀

The platform is now ready to use. Start with test transactions, then switch to live mode when ready.
