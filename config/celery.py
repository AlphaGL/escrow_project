"""
Celery configuration for async tasks (auto-release, notifications, etc.)
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('trustescrow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic Tasks
app.conf.beat_schedule = {
    'check-auto-release-transactions': {
        'task': 'transactions.tasks.check_auto_release',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-pending-notifications': {
        'task': 'transactions.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
