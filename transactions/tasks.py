"""
Celery tasks for transaction automation
- Auto-release funds after deadline
- Send notifications
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Transaction


@shared_task
def check_auto_release():
    """
    Check for transactions that should be auto-released
    Runs every 30 minutes via Celery Beat
    """
    now = timezone.now()
    
    # Find completed transactions past auto-release date
    transactions = Transaction.objects.filter(
        status='COMPLETED',
        is_disputed=False,
        auto_release_date__lte=now
    )
    
    count = 0
    for transaction in transactions:
        # Auto-release the payment
        success = transaction.release_payment()
        if success:
            count += 1
            
            # Send notifications
            send_auto_release_notification.delay(transaction.id)
    
    return f"Auto-released {count} transactions"


@shared_task
def send_auto_release_notification(transaction_id):
    """Send email notification for auto-released payment"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Email to client
        send_mail(
            subject=f'Payment Auto-Released - {transaction.reference}',
            message=f'''
Dear {transaction.client.get_full_name()},

The payment for transaction {transaction.reference} has been automatically released to {transaction.service_provider.get_full_name()}.

Amount Released: ₦{transaction.service_provider_amount:,.2f}
Service: {transaction.service_description}

You did not raise any disputes within the {settings.AUTO_RELEASE_DAYS}-day review period.

Thank you for using TrustEscrow Nigeria!

Best regards,
The TrustEscrow Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[transaction.client.email],
            fail_silently=True,
        )
        
        # Email to provider
        send_mail(
            subject=f'Payment Received - {transaction.reference}',
            message=f'''
Dear {transaction.service_provider.get_full_name()},

Congratulations! You have received payment for transaction {transaction.reference}.

Amount Received: ₦{transaction.service_provider_amount:,.2f}
Service: {transaction.service_description}
Client: {transaction.client.get_full_name()}

The funds are now available in your wallet.

Thank you for using TrustEscrow Nigeria!

Best regards,
The TrustEscrow Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[transaction.service_provider.email],
            fail_silently=True,
        )
        
    except Transaction.DoesNotExist:
        pass


@shared_task
def send_pending_notifications():
    """
    Send reminder notifications for pending actions
    Runs every 15 minutes
    """
    now = timezone.now()
    
    # Remind clients about pending approvals
    pending_approvals = Transaction.objects.filter(
        status='COMPLETED',
        is_disputed=False
    )
    
    for transaction in pending_approvals:
        days_remaining = (transaction.auto_release_date - now).days
        
        # Send reminder 2 days before auto-release
        if days_remaining == 2:
            send_mail(
                subject=f'Action Required - {transaction.reference}',
                message=f'''
Dear {transaction.client.get_full_name()},

Your service provider has completed the work for transaction {transaction.reference}.

Service: {transaction.service_description}
Amount: ₦{transaction.amount:,.2f}

Please review and approve or raise a dispute within {days_remaining} days.
After that, the payment will be automatically released.

Review now: {settings.SITE_URL}/transactions/{transaction.id}/

Best regards,
The TrustEscrow Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.client.email],
                fail_silently=True,
            )


@shared_task
def send_transaction_notification(transaction_id, event_type):
    """
    Send notification for various transaction events
    event_type: 'created', 'paid', 'started', 'completed', 'disputed', 'released'
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        if event_type == 'created':
            # Notify provider about new job
            send_mail(
                subject=f'New Job Request - {transaction.reference}',
                message=f'''
Dear {transaction.service_provider.get_full_name()},

You have a new job request from {transaction.client.get_full_name()}.

Service: {transaction.service_description}
Amount: ₦{transaction.amount:,.2f}
Your Earnings (after fees): ₦{transaction.service_provider_amount:,.2f}

View details: {settings.SITE_URL}/transactions/{transaction.id}/

Best regards,
The TrustEscrow Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.service_provider.email],
                fail_silently=True,
            )
        
        elif event_type == 'paid':
            # Notify both parties
            send_mail(
                subject=f'Payment Secured - {transaction.reference}',
                message=f'''
Dear {transaction.client.get_full_name()},

Your payment of ₦{transaction.amount:,.2f} has been secured in escrow.

The service provider will now begin work.

View transaction: {settings.SITE_URL}/transactions/{transaction.id}/

Best regards,
The TrustEscrow Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.client.email],
                fail_silently=True,
            )
        
        elif event_type == 'completed':
            # Notify client to review
            send_mail(
                subject=f'Work Completed - Action Required - {transaction.reference}',
                message=f'''
Dear {transaction.client.get_full_name()},

{transaction.service_provider.get_full_name()} has marked your service as completed.

Please review the work and:
- Approve to release payment, OR
- Raise a dispute if unsatisfied

Auto-release in {settings.AUTO_RELEASE_DAYS} days if no action taken.

Review now: {settings.SITE_URL}/transactions/{transaction.id}/

Best regards,
The TrustEscrow Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transaction.client.email],
                fail_silently=True,
            )
        
    except Transaction.DoesNotExist:
        pass
