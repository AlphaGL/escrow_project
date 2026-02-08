"""
URL patterns for transactions app
"""
from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('create/', views.create_transaction, name='create'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('<int:transaction_id>/', views.transaction_detail, name='detail'),
    path('<int:transaction_id>/start-work/', views.start_work, name='start_work'),
    path('<int:transaction_id>/complete-work/', views.complete_work, name='complete_work'),
    path('<int:transaction_id>/approve/', views.approve_payment, name='approve'),
    path('<int:transaction_id>/dispute/', views.raise_dispute, name='dispute'),
    path('<int:transaction_id>/send-message/', views.send_message, name='send_message'),
]
