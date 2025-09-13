from django_filters import FilterSet

from store.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'category_id': ['exact'],
            'price': ['lt', 'gt'],
        }
