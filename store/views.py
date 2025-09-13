from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Customer, CustomerImage, Product
from .permissions import IsOwnerOrAdmin
from .serializers import CustomerImageSerializer, CustomerSerializer, ProductSerializer, UpdateCustomerSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related(
        'user').prefetch_related('image').all()
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


class CustomerImageViewSet(ModelViewSet):
    serializer_class = CustomerImageSerializer

    # send the customer_id to serializer
    def get_serializer_context(self):
        return {'customer_id': self.kwargs['customer_pk']}
    
    def get_queryset(self):
        return CustomerImage.objects.filter(customer_id=self.kwargs['customer_pk'])
    

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('images').all()

