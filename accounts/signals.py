"""
Signal handlers for accounts app
Automatically creates wallet when user is created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserWallet


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Create wallet automatically when a new user is created"""
    if created:
        UserWallet.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    """Ensure wallet exists for user"""
    if not hasattr(instance, 'wallet'):
        UserWallet.objects.create(user=instance)
