
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_not_admin_user(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        if not user.is_staff:
            Customer.objects.create(user=user)
            

@receiver(user_logged_in, sender=settings.AUTH_USER_MODEL)            
def attach_cart_to_logged_in_user_if_available(sender, request, user, **kwargs): 
    # check if sessions has a cart_id   
    cart_id = request.session.get('cart_id')
    if cart_id:
        from store.models import Cart
        try:
            cart = Cart.objects.filter(pk=cart_id).first()
            cart.customer = user.customer
            cart.save()
            del request.session['cart_id']
        except Cart.DoesNotExist:
            pass
            
               
