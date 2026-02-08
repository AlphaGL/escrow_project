"""
Forms for creating and managing transactions
"""
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Transaction, TransactionMessage

User = get_user_model()


class CreateTransactionForm(forms.ModelForm):
    """Form for clients to create a new escrow transaction"""
    
    service_provider_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'provider@example.com'
        }),
        help_text="Service provider's email address"
    )
    
    service_provider_phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '08012345678'
        }),
        help_text="Service provider's phone number"
    )
    
    class Meta:
        model = Transaction
        fields = ['amount', 'service_description', 'service_category']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10000',
                'min': settings.MIN_TRANSACTION_AMOUNT,
                'max': settings.MAX_TRANSACTION_AMOUNT,
                'step': '100'
            }),
            'service_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the service you need...'
            }),
            'service_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Web Design, Plumbing, Graphics'
            }),
        }
    
    def clean_amount(self):
        """Validate transaction amount"""
        amount = self.cleaned_data.get('amount')
        if amount < settings.MIN_TRANSACTION_AMOUNT:
            raise forms.ValidationError(
                f'Minimum transaction amount is ₦{settings.MIN_TRANSACTION_AMOUNT:,.2f}'
            )
        if amount > settings.MAX_TRANSACTION_AMOUNT:
            raise forms.ValidationError(
                f'Maximum transaction amount is ₦{settings.MAX_TRANSACTION_AMOUNT:,.2f}'
            )
        return amount
    
    def clean(self):
        """Validate service provider identification"""
        cleaned_data = super().clean()
        email = cleaned_data.get('service_provider_email')
        phone = cleaned_data.get('service_provider_phone')
        
        if not email and not phone:
            raise forms.ValidationError(
                'Please provide either email or phone number of the service provider'
            )
        
        # Find service provider
        provider = None
        if email:
            try:
                provider = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    f'No user found with email: {email}'
                )
        elif phone:
            try:
                provider = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    f'No user found with phone: {phone}'
                )
        
        if provider:
            cleaned_data['service_provider'] = provider
        
        return cleaned_data


class DisputeForm(forms.Form):
    """Form for raising a dispute"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Explain why you are raising this dispute...'
        }),
        help_text='Provide detailed information about the issue'
    )


class ResolveDisputeForm(forms.Form):
    """Admin form for resolving disputes"""
    RESOLUTION_CHOICES = [
        ('full_refund', 'Full Refund to Client (100%)'),
        ('full_payment', 'Full Payment to Provider (0% refund)'),
        ('partial', 'Partial Refund'),
    ]
    
    resolution = forms.ChoiceField(
        choices=RESOLUTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    refund_percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '50'
        }),
        help_text='Only required for partial refund (0-100%)'
    )
    
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Resolution notes...'
        }),
        help_text='Internal notes about the resolution'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        resolution = cleaned_data.get('resolution')
        refund_pct = cleaned_data.get('refund_percentage')
        
        if resolution == 'partial' and refund_pct is None:
            raise forms.ValidationError(
                'Refund percentage is required for partial refunds'
            )
        
        return cleaned_data


class TransactionMessageForm(forms.ModelForm):
    """Form for sending messages in transaction"""
    class Meta:
        model = TransactionMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
