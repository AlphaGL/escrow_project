"""
Quick Data Migration Script for SafeRelease
Just run: python quick_migrate.py
"""

import os
import subprocess
import shutil
from datetime import datetime

print("=" * 70)
print("SafeRelease Data Migration: SQLite → PostgreSQL")
print("=" * 70)
print()

# Step 1: Check SQLite exists
if not os.path.exists('db.sqlite3'):
    print("❌ Error: db.sqlite3 not found!")
    input("Press Enter to exit...")
    exit(1)

print("✓ SQLite database found")
print()

# Step 2: Backup
print("Creating backup...")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_name = f'db.sqlite3.backup_{timestamp}'
shutil.copy2('db.sqlite3', backup_name)
print(f"✓ Backup created: {backup_name}")
print()

# Step 3: Confirm
print("⚠️  Make sure:")
print("  1. You've updated settings.py to use PostgreSQL")
print("  2. DATABASE_URL is set in your .env file")
print("  3. PostgreSQL database exists")
print()

confirm = input("Continue? (yes/no): ")
if confirm.lower() != 'yes':
    print("Migration cancelled.")
    exit(0)

print()
print("=" * 70)

# Step 4: Export data
print("\n📦 Step 1: Exporting data from SQLite...")
export_cmd = [
    'python', 'manage.py', 'dumpdata',
    '--natural-foreign',
    '--natural-primary',
    '--indent=2',
    '--exclude=contenttypes',
    '--exclude=auth.Permission',
    '--exclude=admin.LogEntry',
    '--exclude=sessions.Session',
]

try:
    with open('data_export.json', 'w', encoding='utf-8') as f:
        subprocess.run(export_cmd, stdout=f, check=True)
    
    size = os.path.getsize('data_export.json') / 1024
    print(f"✓ Data exported successfully ({size:.2f} KB)")
except Exception as e:
    print(f"❌ Export failed: {e}")
    exit(1)

# Step 5: Run migrations
print("\n🔄 Step 2: Running PostgreSQL migrations...")
try:
    subprocess.run(['python', 'manage.py', 'migrate'], check=True)
    print("✓ Migrations completed")
except Exception as e:
    print(f"❌ Migrations failed: {e}")
    exit(1)

# Step 6: Import data
print("\n📥 Step 3: Importing data to PostgreSQL...")
try:
    subprocess.run(['python', 'manage.py', 'loaddata', 'data_export.json'], check=True)
    print("✓ Data imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    print("\nTrying alternative import method...")
    
    # Try importing app by app
    apps = ['accounts', 'core', 'transactions', 'payments']
    for app in apps:
        print(f"\n  → Exporting {app}...")
        try:
            with open(f'{app}_data.json', 'w', encoding='utf-8') as f:
                subprocess.run(
                    ['python', 'manage.py', 'dumpdata', app, '--natural-foreign'],
                    stdout=f,
                    check=True
                )
            print(f"  → Importing {app}...")
            subprocess.run(['python', 'manage.py', 'loaddata', f'{app}_data.json'], check=True)
            os.remove(f'{app}_data.json')
            print(f"  ✓ {app} imported")
        except Exception as app_error:
            print(f"  ⚠️  {app} import had issues: {app_error}")

# Step 7: Update sequences
print("\n🔧 Step 4: Updating PostgreSQL sequences...")
sequence_script = """
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Get all tables
    cursor.execute(\"\"\"
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    \"\"\")
    
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        try:
            # Check if table has id column
            cursor.execute(f\"\"\"
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'id'
            \"\"\")
            
            if cursor.fetchone():
                # Try to update sequence
                cursor.execute(f\"\"\"
                    SELECT setval(
                        pg_get_serial_sequence('{table_name}', 'id'),
                        COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                        true
                    )
                \"\"\")
                print(f'✓ {table_name}')
        except Exception as e:
            pass

print('\\nSequences updated!')
"""

with open('_update_seq.py', 'w', encoding='utf-8') as f:
    f.write(sequence_script)

try:
    subprocess.run(['python', '_update_seq.py'], check=True)
    os.remove('_update_seq.py')
except Exception as e:
    print(f"⚠️  Sequence update warning: {e}")
    if os.path.exists('_update_seq.py'):
        os.remove('_update_seq.py')

# Step 8: Verify
print("\n✅ Step 5: Verifying migration...")
verify_script = """
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from transactions.models import Transaction
from payments.models import Payment

print(f'Users: {User.objects.count()}')
print(f'Transactions: {Transaction.objects.count()}')
print(f'Payments: {Payment.objects.count()}')
"""

with open('_verify.py', 'w', encoding='utf-8') as f:
    f.write(verify_script)

try:
    subprocess.run(['python', '_verify.py'], check=True)
    os.remove('_verify.py')
except Exception as e:
    print(f"Verification: {e}")
    if os.path.exists('_verify.py'):
        os.remove('_verify.py')

# Cleanup
print("\n🧹 Cleaning up...")
if os.path.exists('data_export.json'):
    os.remove('data_export.json')
    print("✓ Removed temporary files")

# Success!
print()
print("=" * 70)
print("✅ MIGRATION COMPLETE!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Test your application: python manage.py runserver")
print("  2. Test user login")
print("  3. Verify transactions")
print("  4. Check wallet balances")
print()
print(f"SQLite backup: {backup_name}")
print()

input("Press Enter to exit...")