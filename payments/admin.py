"""
Admin configuration for payments
"""
from django.contrib import admin
from .models import Payment, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin"""
    list_display = ['reference', 'user', 'transaction', 'amount', 'status', 
                    'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['reference', 'paystack_reference', 'user__email', 
                     'transaction__reference']
    readonly_fields = ['payment_id', 'reference', 'created_at', 'verified_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('payment_id', 'reference', 'paystack_reference', 
                      'status', 'created_at', 'verified_at')
        }),
        ('Details', {
            'fields': ('user', 'transaction', 'amount', 'currency', 'payment_method')
        }),
        ('Technical', {
            'fields': ('paystack_response', 'authorization_code', 
                      'ip_address', 'user_agent')
        }),
    )


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Payout admin"""
    list_display = ['reference', 'user', 'amount', 'status', 'bank_name', 
                    'created_at']
    list_filter = ['status', 'bank_name', 'created_at']
    search_fields = ['reference', 'transfer_code', 'user__email', 'account_number']
    readonly_fields = ['payout_id', 'reference', 'created_at', 'processed_at']
