from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from core.views import CustomTokenCreateView, CustomUserViewSet, CustomTokenDestroyView


router = DefaultRouter()
router.register('users', CustomUserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    # external-apps urls



    # CRUD operations (register, list, etc)
    path('auth/', include('djoser.urls')),

    # path('auth/', include('djoser.urls.authtoken')),  # token login/logout
    # implement custom views for login and logout instead of using djoser.urls.authtoken
    path('auth/token/logout/', CustomTokenDestroyView.as_view()),
    path('auth/token/login/', CustomTokenCreateView.as_view()),
    path('auth/', include(router.urls)),


    # my-apps urls
    path('store/', include('store.urls')),

]
