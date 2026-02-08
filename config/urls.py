"""
URL Configuration for TrustEscrow Nigeria
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('transactions/', include('transactions.urls', namespace='transactions')),
    path('payments/', include('payments.urls', namespace='payments')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "TrustEscrow Nigeria Admin"
admin.site.site_title = "TrustEscrow Admin Portal"
admin.site.index_title = "Welcome to TrustEscrow Administration"
