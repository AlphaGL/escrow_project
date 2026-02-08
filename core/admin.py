"""
Admin configuration for core app
"""
from django.contrib import admin
from .models import SiteSettings, FAQ, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site settings admin"""
    list_display = ['site_name', 'support_email', 'maintenance_mode', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """FAQ admin"""
    list_display = ['question', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Testimonial admin"""
    list_display = ['name', 'role', 'rating', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_featured', 'created_at']
    search_fields = ['name', 'role', 'content']
    list_editable = ['is_featured']
