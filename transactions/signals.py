"""
Signal handlers for transactions
Automatically creates timeline entries for transaction events
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Transaction, TransactionTimeline


@receiver(post_save, sender=Transaction)
def create_timeline_entry(sender, instance, created, **kwargs):
    """Create timeline entry for status changes"""
    if created:
        TransactionTimeline.objects.create(
            transaction=instance,
            event='Transaction Created',
            description=f'Transaction {instance.reference} created by {instance.client.get_full_name()}',
            created_by=instance.client
        )
    else:
        # Track status changes
        if instance.status == 'PAID' and instance.paid_at:
            TransactionTimeline.objects.get_or_create(
                transaction=instance,
                event='Payment Received',
                defaults={
                    'description': f'₦{instance.amount:,.2f} received and held in escrow',
                    'created_by': instance.client
                }
            )
        elif instance.status == 'IN_PROGRESS' and instance.work_started_at:
            TransactionTimeline.objects.get_or_create(
                transaction=instance,
                event='Work Started',
                defaults={
                    'description': f'{instance.service_provider.get_full_name()} started working on the service',
                    'created_by': instance.service_provider
                }
            )
        elif instance.status == 'COMPLETED' and instance.work_completed_at:
            TransactionTimeline.objects.get_or_create(
                transaction=instance,
                event='Work Completed',
                defaults={
                    'description': f'{instance.service_provider.get_full_name()} marked work as completed',
                    'created_by': instance.service_provider
                }
            )
        elif instance.status == 'DISPUTED' and instance.is_disputed:
            TransactionTimeline.objects.get_or_create(
                transaction=instance,
                event='Dispute Raised',
                defaults={
                    'description': f'Dispute raised by {instance.client.get_full_name()}',
                    'created_by': instance.client
                }
            )
        elif instance.status == 'RELEASED' and instance.released_at:
            TransactionTimeline.objects.get_or_create(
                transaction=instance,
                event='Payment Released',
                defaults={
                    'description': f'₦{instance.service_provider_amount:,.2f} released to {instance.service_provider.get_full_name()}',
                }
            )
