from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.views import Response

from .models import Customer, CustomerImage, Product, ProductImage
from .permissions import IsOwnerOrAdmin
from .serializers import CustomerImageSerializer, CustomerSerializer, ProductImageSerializer, ProductSerializer, UpdateCustomerSerializer


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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer


    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"images": serializer.data})
