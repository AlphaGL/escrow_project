"""
Payment models for Paystack integration
"""
from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    """Payment tracking model"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CARD', 'Debit/Credit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('USSD', 'USSD'),
    ]
    
    # Payment identification
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reference = models.CharField(max_length=100, unique=True)
    paystack_reference = models.CharField(max_length=100, blank=True)
    
    # Related transaction
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # User who made payment
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='CARD'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Paystack response data
    paystack_response = models.JSONField(null=True, blank=True)
    authorization_code = models.CharField(max_length=100, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reference} - ₦{self.amount:,.2f} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Payout(models.Model):
    """Payout/withdrawal tracking"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
    ]
    
    # Payout identification
    payout_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reference = models.CharField(max_length=100, unique=True)
    transfer_code = models.CharField(max_length=100, blank=True)
    
    # User requesting payout
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    
    # Payout details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Bank details (snapshot at time of payout)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)
    account_name = models.CharField(max_length=100)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Paystack response
    paystack_response = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reference} - {self.user} - ₦{self.amount:,.2f}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"OUT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
