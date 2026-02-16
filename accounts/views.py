"""
Views for user authentication and profile management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, UserRating
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    BankDetailsForm, RatingForm
)


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SafeRelease, {user.get_full_name()}! Your account has been created successfully.')
            return redirect('core:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    ratings = UserRating.objects.filter(rated_user=user)
    
    context = {
        'user': user,
        'ratings': ratings,
        'avg_rating': sum([r.rating for r in ratings]) / len(ratings) if ratings else 0,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def bank_details_view(request):
    """Add/edit bank details"""
    if request.method == 'POST':
        form = BankDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your bank details have been saved successfully!')
            return redirect('accounts:profile')
    else:
        form = BankDetailsForm(instance=request.user)
    
    return render(request, 'accounts/bank_details.html', {'form': form})


def public_profile_view(request, user_id):
    """View other user's public profile"""
    user = get_object_or_404(User, id=user_id)
    ratings = UserRating.objects.filter(rated_user=user)
    
    context = {
        'profile_user': user,
        'ratings': ratings,
        'avg_rating': sum([r.rating for r in ratings]) / len(ratings) if ratings else 0,
    }
    return render(request, 'accounts/public_profile.html', context)
