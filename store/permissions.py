from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
 # override has_object_permission because we need to check 
 # the returned object (customer) from the queryset that run in the view
 def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
    