from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, permission_classes
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from core.views import Response
from .models import Cart, Customer, CustomerImage, Product, ProductImage, Review, CartItem
from .permissions import IsOwnerOrAdmin
from .serializers import (
    CartItemSerializer,
    CustomerFavoriteProductSerializer,
    CustomerImageSerializer,
    CustomerSerializer,
    ProductImageSerializer,
    ProductSerializer,
    ReviewSerializer,
    ToggleFavoriteProductSerializer,
    UpdateCustomerSerializer,
    CartItemSerializer,
)
from .pagination import CustomPagination
from .filters import ProductFilter


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related(
        "user").prefetch_related("image").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UpdateCustomerSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrAdmin()]

        return [IsAuthenticated()]
    



class CustomerImageViewSet(ModelViewSet):
    serializer_class = CustomerImageSerializer

    # send the customer_id to serializer
    def get_serializer_context(self):
        return {"customer_id": self.kwargs["customer_pk"]}

    def get_queryset(self):
        return CustomerImage.objects.filter(customer_id=self.kwargs["customer_pk"])


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = (
        Product.objects.prefetch_related(
            "images").select_related("category").all()
    )
    pagination_class = CustomPagination
    # define ways to shortlist queryset: Filter, Search
    # or ordering: sort
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description", "category__title"]
    ordering_fields = ["title", "price"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        elif self.action == 'favorite':
            return [IsAuthenticated()]
        return [permissions.AllowAny()]
    
    # set detail=True because it will get the product_id /products/{pk}/favorite
    @action(detail=True, methods=['post'], serializer_class=ToggleFavoriteProductSerializer)
    def favorite(self, request, *args, **kwargs):
        print(self.request.user, self.request.user.is_authenticated)
        product = self.get_object()
        serializer = self.get_serializer(context={'request': request, 'product': product})
        favorite_item = serializer.save()  # no .is_valid() needed, no input fields

        message = (
            f"Removed '{product.title}' from favorites."
            if favorite_item is None else f"Added '{product.title}' to favorites."
        )
        return Response({"message": message})


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"images": serializer.data})



class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'product_id': self.kwargs['product_pk']}

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            # only allow Owner & Admin of the review to update or delete
            return [IsOwnerOrAdmin()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [permissions.AllowAny()]

    def get_queryset(self):
        product_id = self.kwargs["product_pk"]
        user_id = self.request.user.id
        return (
            Review.objects.select_related("product", 'customer')
            .filter(product_id=product_id, customer__user_id=user_id)
        )
    

class CustomerFavoriteViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        customer = Customer.objects.get(user_id=self.request.user)
        serializer = CustomerFavoriteProductSerializer(customer, context={'request': request})
        return Response(serializer.data)
    
    
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    
    # define def get_queryset(self) so you can get the queryset 
    # depending on if the user is authenticated or not
    def get_queryset(self):
        request = self.request
        
        if request.user.is_authenticated:
            # get the cart from customer
            customer = Customer.objects.filter(user=request.user).first()
            cart = Cart.objects.filter(customer=customer).first()
        else:
            # get cart from session
            cart_id = request.session.get('cart_id')
            cart = Cart.objects.filter(pk=cart_id).first()

            if cart:
                return CartItem.objects.filter(cart=cart)
            else:
                return CartItem.objects.none()
            
            
    
           
