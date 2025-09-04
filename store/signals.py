
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_not_admin_user(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        if not user.is_staff:
            Customer.objects.create(user=user)
