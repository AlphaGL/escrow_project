"""
Context processors for making data available in all templates
"""
from django.conf import settings
from .models import SiteSettings


def site_settings(request):
    """Make site settings available in all templates"""
    try:
        site_config = SiteSettings.objects.first()
    except:
        site_config = None
    
    return {
        'site_config': site_config,
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'TrustEscrow Nigeria'),
        'PAYSTACK_PUBLIC_KEY': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
    }
