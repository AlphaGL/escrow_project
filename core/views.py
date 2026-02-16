"""
Core views for homepage, dashboard, and general pages
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from transactions.models import Transaction
from .models import FAQ, Testimonial
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def love_page(request):
    """
    Displays the romantic message page with access code protection.
    The access code is 'FOREVER' (case-insensitive).
    
    This is a special page created to express feelings to someone special.
    """
    return render(request, 'core/love_page.html')


# Optional: If you want server-side validation instead of JavaScript
@csrf_exempt
def validate_access(request):
    """
    Optional view to validate access code on the server side.
    Returns JSON response indicating if access is granted.
    """
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        
        # The secret access code
        SECRET_CODE = 'FOREVER'
        
        if code == SECRET_CODE:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Incorrect code'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def home(request):
    """Homepage view"""
    if request.user.is_authenticated:
        return dashboard(request)
    
    # Get testimonials and FAQs
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    faqs = FAQ.objects.filter(is_active=True)[:8]
    
    context = {
        'testimonials': testimonials,
        'faqs': faqs,
    }
    
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    
    # Get user's transactions
    as_client = Transaction.objects.filter(client=user)
    as_provider = Transaction.objects.filter(service_provider=user)
    
    # Statistics
    stats = {
        'total_transactions': as_client.count() + as_provider.count(),
        'as_client_count': as_client.count(),
        'as_provider_count': as_provider.count(),
        'active_transactions': Transaction.objects.filter(
            Q(client=user) | Q(service_provider=user),
            status__in=['PAID', 'IN_PROGRESS', 'COMPLETED']
        ).count(),
        'wallet_balance': user.wallet.balance,
        'escrow_balance': user.wallet.escrow_balance,
        'total_earned': user.wallet.total_earned,
        'total_spent': user.wallet.total_spent,
    }
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        Q(client=user) | Q(service_provider=user)
    ).order_by('-created_at')[:5]
    
    # Pending actions
    pending_approvals = Transaction.objects.filter(
        client=user,
        status='COMPLETED',
        is_disputed=False
    ).count()
    
    pending_work = Transaction.objects.filter(
        service_provider=user,
        status__in=['PAID', 'IN_PROGRESS']
    ).count()
    
    context = {
        'stats': stats,
        'recent_transactions': recent_transactions,
        'pending_approvals': pending_approvals,
        'pending_work': pending_work,
    }
    
    return render(request, 'core/dashboard.html', context)


def how_it_works(request):
    """How it works page"""
    return render(request, 'core/how_it_works.html')


def about(request):
    """About us page"""
    return render(request, 'core/about.html')


def faq_page(request):
    """FAQ page"""
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'core/faq.html', {'faqs': faqs})


def contact(request):
    """Contact page"""
    return render(request, 'core/contact.html')


def terms(request):
    """Terms and conditions"""
    return render(request, 'core/terms.html')


def privacy(request):
    """Privacy policy"""
    return render(request, 'core/privacy.html')
