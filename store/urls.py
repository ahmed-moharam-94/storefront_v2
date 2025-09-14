from email.mime import base
from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from store import views


router = DefaultRouter()
router.register("customers", views.CustomerViewSet, basename="customers")
router.register("products", views.ProductViewSet, basename="products")

# Nested Routers #
# define the custom router with (router, parent-prefix, lookup(/{customer_pk}))
# lookup will be used to get the pk in view and maybe send it to serializer ex: customer_pk
customers_nested_router = routers.NestedDefaultRouter(
    router, "customers", lookup="customer"
)
products_nested_router = routers.NestedDefaultRouter(
    router, "products", lookup="product"
)

# register the nested paths with (prefix, ViewSet, basename(name-list, name-detail)
# *basename is required when queryset is not defined in the ViewSet)*
customers_nested_router.register(
    "images", views.CustomerImageViewSet, basename="customer-image"
)
products_nested_router.register(
    "images", views.ProductImageViewSet, basename="product-images"
)
products_nested_router.register('reviews', views.ReviewViewSet, basename='product-review')


urlpatterns = [
    path("", include(router.urls)),
    path("", include(customers_nested_router.urls)),
    path("", include(products_nested_router.urls)),
]

# to define a route:
# 1) Create a router instance with DefaultRouter() for all routes
# 2) Register paths using 'prefix', ViewSet, basename

# to define a nested route:
# 1) Create a nested router instance using routers.NestedDefaultRouter using: router instance (from the DefaultRouter), parent_prefix (same as the parent router prefix), lookup (singular of the prefix)
# 2) Register nested route path in the created nested router using: prefix, ViewSet, basename (singular_parent-singular_prefix)
