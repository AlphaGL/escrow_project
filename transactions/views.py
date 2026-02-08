"""
Views for transaction management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Transaction, TransactionMessage
from .forms import CreateTransactionForm, DisputeForm, TransactionMessageForm
from .tasks import send_transaction_notification


@login_required
def create_transaction(request):
    """Create a new escrow transaction"""
    if request.method == 'POST':
        form = CreateTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.client = request.user
            transaction.service_provider = form.cleaned_data['service_provider']
            
            # Check if client is trying to create transaction with themselves
            if transaction.client == transaction.service_provider:
                messages.error(request, 'You cannot create a transaction with yourself!')
                return render(request, 'transactions/create.html', {'form': form})
            
            transaction.save()
            
            # Send notification to provider
            send_transaction_notification.delay(transaction.id, 'created')
            
            messages.success(
                request,
                f'Transaction {transaction.reference} created! Please proceed to payment.'
            )
            return redirect('payments:initiate', transaction_id=transaction.id)
    else:
        form = CreateTransactionForm()
    
    return render(request, 'transactions/create.html', {'form': form})


@login_required
def transaction_detail(request, transaction_id):
    """View transaction details"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Check if user is involved in transaction
    if request.user not in [transaction.client, transaction.service_provider]:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this transaction.')
            return redirect('core:dashboard')
    
    # Get messages
    transaction_messages = transaction.messages.all()
    
    # Mark messages as read
    unread_messages = transaction_messages.filter(
        is_read=False
    ).exclude(sender=request.user)
    unread_messages.update(is_read=True)
    
    # Message form
    message_form = TransactionMessageForm()
    
    context = {
        'transaction': transaction,
        'messages': transaction_messages,
        'message_form': message_form,
        'timeline': transaction.timeline.all(),
    }
    
    return render(request, 'transactions/detail.html', context)


@login_required
def my_transactions(request):
    """View user's transactions"""
    # Get filter parameter
    filter_type = request.GET.get('filter', 'all')
    
    # Base query
    if filter_type == 'as_client':
        transactions = Transaction.objects.filter(client=request.user)
    elif filter_type == 'as_provider':
        transactions = Transaction.objects.filter(service_provider=request.user)
    else:
        transactions = Transaction.objects.filter(
            Q(client=request.user) | Q(service_provider=request.user)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    transactions = transactions.order_by('-created_at')
    
    context = {
        'transactions': transactions,
        'filter_type': filter_type,
        'selected_status': status,
    }
    
    return render(request, 'transactions/my_transactions.html', context)


@login_required
def start_work(request, transaction_id):
    """Service provider accepts and starts work"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is the service provider
    if request.user != transaction.service_provider:
        messages.error(request, 'Only the service provider can start work.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Verify transaction is paid
    if not transaction.is_paid:
        messages.error(request, 'Transaction must be paid before starting work.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Start work
    if transaction.status == 'PAID':
        transaction.start_work()
        send_transaction_notification.delay(transaction.id, 'started')
        messages.success(request, 'Work started! You can now begin providing the service.')
    else:
        messages.error(request, f'Cannot start work. Current status: {transaction.get_status_display()}')
    
    return redirect('transactions:detail', transaction_id=transaction.id)


@login_required
def complete_work(request, transaction_id):
    """Service provider marks work as completed"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is the service provider
    if request.user != transaction.service_provider:
        messages.error(request, 'Only the service provider can complete work.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Complete work
    if transaction.status == 'IN_PROGRESS':
        transaction.complete_work()
        send_transaction_notification.delay(transaction.id, 'completed')
        messages.success(
            request,
            f'Work marked as completed! Client has {transaction.auto_release_date.date()} to review.'
        )
    else:
        messages.error(request, f'Cannot complete work. Current status: {transaction.get_status_display()}')
    
    return redirect('transactions:detail', transaction_id=transaction.id)


@login_required
def approve_payment(request, transaction_id):
    """Client approves payment release"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is the client
    if request.user != transaction.client:
        messages.error(request, 'Only the client can approve payment.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    # Approve and release payment
    if transaction.status == 'COMPLETED':
        transaction.approve_payment()
        messages.success(
            request,
            f'Payment of ₦{transaction.service_provider_amount:,.2f} released to {transaction.service_provider.get_full_name()}!'
        )
    else:
        messages.error(request, f'Cannot approve payment. Current status: {transaction.get_status_display()}')
    
    return redirect('transactions:detail', transaction_id=transaction.id)


@login_required
def raise_dispute(request, transaction_id):
    """Client raises a dispute"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is the client
    if request.user != transaction.client:
        messages.error(request, 'Only the client can raise a dispute.')
        return redirect('transactions:detail', transaction_id=transaction.id)
    
    if request.method == 'POST':
        form = DisputeForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            transaction.raise_dispute(reason)
            send_transaction_notification.delay(transaction.id, 'disputed')
            messages.warning(
                request,
                'Dispute raised. Our admin team will review and resolve within 3-5 business days.'
            )
            return redirect('transactions:detail', transaction_id=transaction.id)
    else:
        form = DisputeForm()
    
    return render(request, 'transactions/raise_dispute.html', {
        'form': form,
        'transaction': transaction
    })


@login_required
def send_message(request, transaction_id):
    """Send a message in transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify user is involved
    if request.user not in [transaction.client, transaction.service_provider]:
        messages.error(request, 'You cannot send messages in this transaction.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = TransactionMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.transaction = transaction
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent!')
    
    return redirect('transactions:detail', transaction_id=transaction.id)
