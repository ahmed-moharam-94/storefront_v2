from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from core.views import Response
from .models import (
    Cart,
    Customer,
    CustomerImage,
    Order,
    Product,
    ProductImage,
    Review,
    CartItem,
)
from .permissions import IsOwnerOrAdmin, IsCartItemOwnerOrAdmin
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CustomerFavoriteProductSerializer,
    CustomerImageSerializer,
    CustomerSerializer,
    OrderSerializer,
    ProductImageSerializer,
    ProductSerializer,
    ReviewSerializer,
    ToggleFavoriteProductSerializer,
    UpdateCustomerSerializer,
    CartItemSerializer,
    CreateOrderSerializer,
)
from .pagination import CustomPagination
from .filters import ProductFilter
from django.core.cache import cache



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


class ProductViewSet(CacheResponseMixin, ModelViewSet):
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

    cache_response_timeout = 60 * 15  # 15 minutes

    def get_cache_response_timeout(self, view_instance, view_method):
        if view_method == 'list':
            return 60 * 5    # 5 minutes
        elif view_method == 'retrieve':
            return 60 * 60   # 1 hour
        elif view_method == 'favorite':
            return 0         # disable caching
        return self.cache_response_timeout


    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        elif self.action == "favorite":
            return [IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print("SQL queries executed:", len(connection.queries))  
        for q in connection.queries:
            print(q["sql"])
        return response

    # set detail=True because it will get the product_id /products/{pk}/favorite
    @action(
        detail=True, methods=["post"], serializer_class=ToggleFavoriteProductSerializer
    )
    def favorite(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(
            context={"request": request, "product": product}
        )
        favorite_item = serializer.save()  # no .is_valid() needed, no input fields

        message = (
            f"Removed '{product.title}' from favorites."
            if favorite_item is None
            else f"Added '{product.title}' to favorites."
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
        return {"request": self.request, "product_id": self.kwargs["product_pk"]}

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            # only allow Owner & Admin of the review to update or delete
            return [IsOwnerOrAdmin()]
        elif self.action == "create":
            return [IsAuthenticated()]
        else:
            return [permissions.AllowAny()]

    def get_queryset(self):
        product_id = self.kwargs["product_pk"]
        user_id = self.request.user.id
        return Review.objects.select_related("product", "customer").filter(
            product_id=product_id, customer__user_id=user_id
        )


class CustomerFavoriteViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        customer = Customer.objects.get(user_id=self.request.user)
        serializer = CustomerFavoriteProductSerializer(
            customer, context={"request": request}
        )
        return Response(serializer.data)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer

    def get_permissions(self):
        # Everyone can create/list their cart items
        if self.action in ["create", "list"]:
            return [AllowAny()]
        # Updates/deletes require ownership check
        return [IsCartItemOwnerOrAdmin()]

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
            cart_id = request.session.get("cart_id")
            print(f'cart_id:: {cart_id}')
            cart = Cart.objects.filter(pk=cart_id).first()

        if cart:
            return CartItem.objects.select_related("product").filter(cart=cart)
        else:
            return CartItem.objects.none()


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_permissions(self):
        if self.action in ["list", "destroy"]:
            return [IsAdminUser()]
        return [IsOwnerOrAdmin()]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related(
        'items__product').prefetch_related('items__product__image').all()
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'OPTIONS':
            return [permissions.AllowAny()]
        elif self.action in ['create_order', 'options']:
            return [IsAuthenticated()]
        elif self.action == 'list':
            return [IsOwnerOrAdmin()]
        return [IsAdminUser()]
    

    def get_queryset(self):
        # check if the user is admin then get all orders
        if self.request.user.is_staff:
            return Order.objects.select_related('customer').prefetch_related('items__product').all()

        # if the user is not admin only get his orders
        customer_id = Customer.objects.only(
            'id').get(user_id=self.request.user.id)

        return Order.objects.prefetch_related('items__product').filter(customer_id=customer_id).all()

    @action(detail=False, methods=['post'], serializer_class=CreateOrderSerializer, url_path='create-order')
    def create_order(self, request, *args, **kwargs):
        # input serializer
        serializer = self.get_serializer(
            context={
                'request': request,
            })
        order = serializer.save()
        # output serializer
        order_serializer = OrderSerializer(order, context={'request': request})
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)



def test_redis():
    cache.set('test_key', 'test_value', 60)
    value = cache.get('test_key')
    print(f"Cache test: {value}")
    return value