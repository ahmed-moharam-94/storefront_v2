from rest_framework.permissions import BasePermission

from store.models import Customer


class IsOwnerOrAdmin(BasePermission):
    # override has_object_permission because we need to check
    # the returned object (customer) from the queryset that run in the view
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class IsCartItemOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            # admin can do everything
            return True
        elif request.user.is_authenticated:
            # authenticated user can update/delete their items only
            customer = Customer.objects.get(user=request.user)
            return obj.cart.customer == customer
        else:
            # unauthenticated users can update/delete items form cart in the session
            session_cart_id = request.session.get("cart_id")
            return str(obj.cart.id) == str(session_cart_id)
