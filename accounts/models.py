"""
Custom User Model for TrustEscrow Nigeria
Supports both clients and service providers
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Custom user model with extended fields"""
    
    USER_TYPE_CHOICES = [
        ('CLIENT', 'Client'),
        ('PROVIDER', 'Service Provider'),
        ('BOTH', 'Both'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?234?\d{10,11}$',
        message="Phone number must be in format: '+2348012345678' or '08012345678'"
    )
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        help_text="Nigerian phone number"
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='BOTH'
    )
    
    # Profile fields
    profile_image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        default='profiles/default.png'
    )
    bio = models.TextField(max_length=500, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # Bank details (for service providers)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=10, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    
    # Trust score
    trust_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Trust score from 0.00 to 5.00"
    )
    total_completed_transactions = models.PositiveIntegerField(default=0)
    total_disputes = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return user's full name or username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def update_trust_score(self):
        """Calculate and update trust score based on transactions"""
        if self.total_completed_transactions == 0:
            self.trust_score = 0.00
        else:
            # Simple algorithm: 5.0 base - (disputes/transactions * 5)
            dispute_ratio = self.total_disputes / self.total_completed_transactions
            self.trust_score = max(0, 5.0 - (dispute_ratio * 5))
        self.save()


class UserWallet(models.Model):
    """User wallet for storing balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Available balance in Naira"
    )
    escrow_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Money held in escrow"
    )
    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Wallet'
        verbose_name_plural = 'User Wallets'
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Wallet - ₦{self.balance:,.2f}"


class UserRating(models.Model):
    """Ratings and reviews for users"""
    rated_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_ratings'
    )
    rater = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    review = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Ratings'
        unique_together = ['transaction', 'rater']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rater} rated {self.rated_user} - {self.rating} stars"
