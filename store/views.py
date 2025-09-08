from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from.models import Customer
from.permissions import IsOwnerOrAdmin
from.serializers import CustomerSerializer, UpdateCustomerSerializer

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateCustomerSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()] 
        
        return [IsAuthenticated()]
    
