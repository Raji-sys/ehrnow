import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Paypoint, Dispensary

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Paypoint)
def update_dispensary_on_payment_confirmation(sender, instance, **kwargs):
    logger.info(f"Post-save signal triggered for Paypoint {instance.id}, status: {instance.status}")
    if instance.status:  # Check if the payment status is True
        logger.info(f"Paypoint {instance.id} status is now True. Updating dispensary records.")
        dispensaries = Dispensary.objects.filter(payment=instance)
        for dispensary in dispensaries:
            # Ensure the quantity is not deducted more than once
            if not dispensary.quantity_deducted:
                logger.info(f"Updating drug quantities for dispensary {dispensary.id}")
                dispensary.drug.total_purchased_quantity -= dispensary.quantity
                dispensary.drug.total_issued += dispensary.quantity
                dispensary.drug.save()
                dispensary.quantity_deducted = True
                dispensary.save()
            else:
                logger.warning(f"Quantity already deducted for dispensary {dispensary.id}")
