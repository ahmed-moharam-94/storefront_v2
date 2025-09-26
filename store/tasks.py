from celery import shared_task
from django.db.models import F, Count
from .models import Product, Cart


@shared_task
def update_products_prices():
    Product.objects.update(price=F('price') + 1)
    print("All product prices increased by 1")


@shared_task
def delete_empty_carts():
    Cart.objects\
        .annotate(items_count=Count("cart_items"))\
        .filter(items_count=0).delete()
    print("Deleted all empty carts")
