"""
Views for payment processing with Paystack
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from transactions.models import Transaction
from .models import Payment
from .paystack import paystack


@login_required
def initiate_payment(request, transaction_id):
    """Initiate payment for a transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is the client
    if request.user != transaction.client:
        messages.error(request, 'Only the client can make payment.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Check if already paid
    if transaction.is_paid:
        messages.warning(request, 'This transaction has already been paid for.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Create payment record
    payment = Payment.objects.create(
        transaction=transaction,
        user=request.user,
        amount=transaction.amount,
    )
    
    # Get client IP and user agent
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        payment.ip_address = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else:
        payment.ip_address = request.META.get('REMOTE_ADDR')
    payment.user_agent = request.META.get('HTTP_USER_AGENT', '')
    payment.save()
    
    # Initialize Paystack payment
    response = paystack.initialize_payment(
        email=request.user.email,
        amount=payment.amount,
        reference=payment.reference,
        callback_url=f"{settings.SITE_URL}/payments/verify/?reference={payment.reference}"
    )
    
    if response.get('status'):
        # Save Paystack reference
        payment.paystack_reference = response['data']['reference']
        payment.save()
        
        # Redirect to Paystack payment page
        authorization_url = response['data']['authorization_url']
        return redirect(authorization_url)
    else:
        payment.status = 'FAILED'
        payment.save()
        messages.error(request, f"Payment initialization failed: {response.get('message')}")
        return redirect('transactions:detail', transaction_id=transaction.id)


@csrf_exempt
def verify_payment(request):
    """Verify payment from Paystack callback"""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Payment reference not found.')
        return redirect('core:dashboard')
    
    # Get payment record
    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
        return redirect('core:dashboard')
    
    # Verify with Paystack
    response = paystack.verify_payment(reference)
    
    if response.get('status') and response['data']['status'] == 'success':
        # Payment successful
        payment.status = 'SUCCESS'
        payment.verified_at = timezone.now()
        payment.paystack_response = response['data']
        payment.authorization_code = response['data'].get('authorization', {}).get('authorization_code', '')
        payment.save()
        
        # Mark transaction as paid
        payment.transaction.mark_as_paid(reference)
        
        messages.success(
            request,
            f'Payment successful! ₦{payment.amount:,.2f} is now safely held in escrow.'
        )
        return redirect('transactions:detail', transaction_id=payment.transaction.id)
    else:
        # Payment failed
        payment.status = 'FAILED'
        payment.paystack_response = response.get('data', {})
        payment.save()
        
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('transactions:detail', transaction_id=payment.transaction.id)


@csrf_exempt
def paystack_webhook(request):
    """
    Webhook endpoint for Paystack events
    This allows Paystack to notify us about payment events
    """
    if request.method == 'POST':
        import json
        import hmac
        import hashlib
        
        # Verify webhook signature
        paystack_signature = request.headers.get('X-Paystack-Signature')
        body = request.body
        
        # Compute hash
        computed_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            body,
            hashlib.sha512
        ).hexdigest()
        
        if paystack_signature != computed_signature:
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
        
        # Process event
        try:
            data = json.loads(body)
            event = data.get('event')
            event_data = data.get('data', {})
            
            if event == 'charge.success':
                # Handle successful payment
                reference = event_data.get('reference')
                try:
                    payment = Payment.objects.get(paystack_reference=reference)
                    if payment.status != 'SUCCESS':
                        payment.status = 'SUCCESS'
                        payment.verified_at = timezone.now()
                        payment.paystack_response = event_data
                        payment.save()
                        payment.transaction.mark_as_paid(reference)
                except Payment.DoesNotExist:
                    pass
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@login_required
def payment_history(request):
    """View user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/history.html', context)
