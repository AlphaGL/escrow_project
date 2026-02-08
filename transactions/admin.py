"""
Admin configuration for transactions
"""
from django.contrib import admin
from .models import Transaction, TransactionMessage, TransactionTimeline
from .forms import ResolveDisputeForm


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Transaction admin with dispute resolution"""
    list_display = ['reference', 'client', 'service_provider', 'amount', 
                    'status', 'is_disputed', 'created_at']
    list_filter = ['status', 'is_disputed', 'created_at']
    search_fields = ['reference', 'client__email', 'service_provider__email', 
                     'service_description']
    readonly_fields = ['transaction_id', 'reference', 'created_at', 'paid_at',
                       'work_started_at', 'work_completed_at', 'released_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction_id', 'reference', 'status', 'created_at')
        }),
        ('Parties', {
            'fields': ('client', 'service_provider')
        }),
        ('Financial', {
            'fields': ('amount', 'platform_fee', 'service_provider_amount', 
                      'payment_reference', 'is_paid')
        }),
        ('Service Details', {
            'fields': ('service_description', 'service_category')
        }),
        ('Timeline', {
            'fields': ('paid_at', 'work_started_at', 'work_completed_at', 
                      'approved_at', 'released_at', 'auto_release_date')
        }),
        ('Dispute', {
            'fields': ('is_disputed', 'dispute_reason', 'dispute_raised_at',
                      'dispute_resolved_at', 'admin_notes')
        }),
    )
    
    def resolve_dispute(self, request, queryset):
        """Custom admin action to resolve disputes"""
        # This would open a custom form
        pass
    
    actions = ['resolve_dispute']


@admin.register(TransactionMessage)
class TransactionMessageAdmin(admin.ModelAdmin):
    """Transaction messages admin"""
    list_display = ['transaction', 'sender', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['transaction__reference', 'sender__email', 'message']
    readonly_fields = ['created_at']


@admin.register(TransactionTimeline)
class TransactionTimelineAdmin(admin.ModelAdmin):
    """Transaction timeline admin"""
    list_display = ['transaction', 'event', 'created_at', 'created_by']
    list_filter = ['event', 'created_at']
    search_fields = ['transaction__reference', 'event', 'description']
    readonly_fields = ['created_at']
