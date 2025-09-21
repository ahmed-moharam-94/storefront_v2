
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Cart, Customer
from store.signals import user_logged_in_signal, order_created_signal

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_not_admin_user(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        if not user.is_staff:
            Customer.objects.create(user=user)
            

@receiver(user_logged_in_signal)
def attach_or_merge_cart_to_logged_in_user_if_available(sender, request, user, **kwargs):
    print('attach_or_merge_cart_to_logged_in_user_if_available called')

    cart_id_from_session = request.session.get('cart_id')
    customer = Customer.objects.get(user=user)

    cart_from_customer = Cart.objects.filter(customer=customer).first()
    cart_from_session = Cart.objects.filter(pk=cart_id_from_session).first() if cart_id_from_session else None

    if cart_from_customer and cart_from_session:
        # merge items from session cart into customer cart
        for item in cart_from_session.cart_items.all():
            # handle same product in both carts
            existing_item = cart_from_customer.cart_items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = cart_from_customer
                item.save()

        cart_from_session.delete()

    elif not cart_from_customer and cart_from_session:
        # no existing customer cart → just assign session cart
        cart_from_session.customer = customer
        cart_from_session.save()

    # Always remove session cart reference after login
    if 'cart_id' in request.session:
        del request.session['cart_id']

@receiver(order_created_signal)
def order_create(sender, request, user, order, **kwargs):
    print(f'Order {order.id} is created by user {user.id}')

            
               
