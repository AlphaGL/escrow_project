"""
Transaction models for escrow system
Handles the entire escrow workflow
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class Transaction(models.Model):
    """Main transaction model for escrow"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid - In Escrow'),
        ('IN_PROGRESS', 'Work In Progress'),
        ('COMPLETED', 'Work Completed'),
        ('APPROVED', 'Payment Approved'),
        ('RELEASED', 'Payment Released'),
        ('DISPUTED', 'Disputed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Unique identifier
    transaction_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    reference = models.CharField(
        max_length=50,
        unique=True,
        help_text="Human-readable reference"
    )
    
    # Parties involved
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions_as_client'
    )
    service_provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions_as_provider'
    )
    
    # Transaction details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount in Naira"
    )
    platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    service_provider_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount provider receives after fees"
    )
    
    # Service description
    service_description = models.TextField(
        max_length=1000,
        help_text="Description of service to be provided"
    )
    service_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category of service (e.g., Web Design, Plumbing)"
    )
    
    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Important dates
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)
    work_completed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    auto_release_date = models.DateTimeField(null=True, blank=True)
    
    # Dispute handling
    is_disputed = models.BooleanField(default=False)
    dispute_reason = models.TextField(blank=True)
    dispute_raised_at = models.DateTimeField(null=True, blank=True)
    dispute_resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Payment tracking
    payment_reference = models.CharField(max_length=100, blank=True)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.client} → {self.service_provider}"
    
    def save(self, *args, **kwargs):
        # Generate reference if not exists
        if not self.reference:
            self.reference = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate platform fee and provider amount
        if not self.platform_fee:
            self.platform_fee = (self.amount * settings.PLATFORM_FEE_PERCENTAGE) / 100
            self.service_provider_amount = self.amount - self.platform_fee
        
        # Set auto-release date when work is completed
        if self.status == 'COMPLETED' and not self.auto_release_date:
            self.auto_release_date = timezone.now() + timedelta(days=settings.AUTO_RELEASE_DAYS)
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self, payment_ref):
        """Mark transaction as paid and move to escrow"""
        self.is_paid = True
        self.status = 'PAID'
        self.paid_at = timezone.now()
        self.payment_reference = payment_ref
        self.save()
        
        # Update client wallet escrow balance
        self.client.wallet.escrow_balance += self.amount
        self.client.wallet.total_spent += self.amount
        self.client.wallet.save()
    
    def start_work(self):
        """Service provider accepts and starts work"""
        self.status = 'IN_PROGRESS'
        self.work_started_at = timezone.now()
        self.save()
    
    def complete_work(self):
        """Service provider marks work as completed"""
        self.status = 'COMPLETED'
        self.work_completed_at = timezone.now()
        self.auto_release_date = timezone.now() + timedelta(days=settings.AUTO_RELEASE_DAYS)
        self.save()
    
    def approve_payment(self):
        """Client approves payment release"""
        self.status = 'APPROVED'
        self.approved_at = timezone.now()
        self.save()
        self.release_payment()
    
    def release_payment(self):
        """Release payment to service provider"""
        if self.status not in ['APPROVED', 'COMPLETED']:
            return False
        
        # Update status
        self.status = 'RELEASED'
        self.released_at = timezone.now()
        
        # Transfer from escrow to provider's wallet
        self.client.wallet.escrow_balance -= self.amount
        self.client.wallet.save()
        
        self.service_provider.wallet.balance += self.service_provider_amount
        self.service_provider.wallet.total_earned += self.service_provider_amount
        self.service_provider.wallet.save()
        
        # Update user stats
        self.client.total_completed_transactions += 1
        self.client.save()
        
        self.service_provider.total_completed_transactions += 1
        self.service_provider.update_trust_score()
        
        self.save()
        return True
    
    def raise_dispute(self, reason):
        """Client raises a dispute"""
        self.is_disputed = True
        self.status = 'DISPUTED'
        self.dispute_reason = reason
        self.dispute_raised_at = timezone.now()
        self.save()
        
        # Update stats
        self.service_provider.total_disputes += 1
        self.service_provider.update_trust_score()
    
    def resolve_dispute(self, resolution, refund_percentage=0):
        """Admin resolves dispute"""
        self.is_disputed = False
        self.dispute_resolved_at = timezone.now()
        
        if refund_percentage == 100:
            # Full refund to client
            self.status = 'REFUNDED'
            self.client.wallet.escrow_balance -= self.amount
            self.client.wallet.balance += self.amount
            self.client.wallet.save()
        elif refund_percentage == 0:
            # Full payment to provider
            self.approve_payment()
        else:
            # Partial refund
            refund_amount = (self.amount * refund_percentage) / 100
            provider_amount = self.amount - refund_amount
            
            self.client.wallet.escrow_balance -= self.amount
            self.client.wallet.balance += refund_amount
            self.client.wallet.save()
            
            self.service_provider.wallet.balance += provider_amount
            self.service_provider.wallet.save()
            
            self.status = 'RELEASED'
        
        self.save()


class TransactionMessage(models.Model):
    """Messages between client and provider for a transaction"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField(max_length=2000)
    attachment = models.FileField(
        upload_to='transaction_attachments/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Transaction Message'
        verbose_name_plural = 'Transaction Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender} → {self.transaction.reference}"


class TransactionTimeline(models.Model):
    """Timeline/audit log for transaction events"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='timeline'
    )
    event = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Transaction Timeline'
        verbose_name_plural = 'Transaction Timelines'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.transaction.reference} - {self.event}"
