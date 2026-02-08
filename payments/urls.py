"""
URL patterns for payments app
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:transaction_id>/', views.initiate_payment, name='initiate'),
    path('verify/', views.verify_payment, name='verify'),
    path('webhook/', views.paystack_webhook, name='webhook'),
    path('history/', views.payment_history, name='history'),
]
