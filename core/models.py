"""
Core models for the platform
"""
from django.db import models


class SiteSettings(models.Model):
    """Site-wide settings"""
    site_name = models.CharField(max_length=100, default='TrustEscrow Nigeria')
    site_description = models.TextField(default='Secure escrow payments for services')
    site_logo = models.ImageField(upload_to='site/', null=True, blank=True)
    
    # Contact info
    support_email = models.EmailField(default='support@trustescrow.ng')
    support_phone = models.CharField(max_length=20, default='+234 800 000 0000')
    
    # Social media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Features
    maintenance_mode = models.BooleanField(default=False)
    allow_new_registrations = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name


class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """User testimonials"""
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text='e.g., Freelance Designer')
    content = models.TextField(max_length=500)
    avatar = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.role}"
