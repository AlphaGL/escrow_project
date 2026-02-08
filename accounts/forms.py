"""
Forms for user authentication and profile management
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserRating

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '08012345678'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'first_name', 'last_name', 
                  'user_type', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0]
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'bio', 
                  'profile_image', 'user_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }


class BankDetailsForm(forms.ModelForm):
    """Form for adding bank details"""
    class Meta:
        model = User
        fields = ['bank_name', 'account_number', 'account_name']
        widgets = {
            'bank_name': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Bank'),
                ('Access Bank', 'Access Bank'),
                ('GTBank', 'Guaranty Trust Bank'),
                ('First Bank', 'First Bank of Nigeria'),
                ('UBA', 'United Bank for Africa'),
                ('Zenith Bank', 'Zenith Bank'),
                ('Stanbic IBTC', 'Stanbic IBTC Bank'),
                ('Sterling Bank', 'Sterling Bank'),
                ('Polaris Bank', 'Polaris Bank'),
                ('Fidelity Bank', 'Fidelity Bank'),
                ('FCMB', 'First City Monument Bank'),
                ('Kuda', 'Kuda Bank'),
                ('OPay', 'OPay'),
                ('PalmPay', 'PalmPay'),
            ]),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890',
                'maxlength': '10'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account Name'
            }),
        }


class RatingForm(forms.ModelForm):
    """Form for rating users after transaction"""
    class Meta:
        model = UserRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '★' * i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience...'
            }),
        }
