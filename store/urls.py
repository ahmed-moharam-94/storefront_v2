from django.urls import include, path
from rest_framework.routers import DefaultRouter

from store import views



router = DefaultRouter()
router.register('customers', views.CustomerViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
