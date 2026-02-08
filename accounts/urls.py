"""
URL patterns for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/bank-details/', views.bank_details_view, name='bank_details'),
    path('user/<int:user_id>/', views.public_profile_view, name='public_profile'),
]
