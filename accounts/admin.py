"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserWallet, UserRating


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = ['email', 'get_full_name', 'phone_number', 'user_type', 
                    'is_verified', 'trust_score', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_staff', 'created_at']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('phone_number', 'user_type', 'profile_image', 'bio')
        }),
        ('Verification', {
            'fields': ('is_verified', 'is_phone_verified', 'is_email_verified')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'account_name')
        }),
        ('Trust Metrics', {
            'fields': ('trust_score', 'total_completed_transactions', 'total_disputes')
        }),
    )


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    """User Wallet admin"""
    list_display = ['user', 'balance', 'escrow_balance', 'total_earned', 'updated_at']
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['created_at']


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    """User Rating admin"""
    list_display = ['rated_user', 'rater', 'rating', 'transaction', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['rated_user__email', 'rater__email']
    readonly_fields = ['created_at']
