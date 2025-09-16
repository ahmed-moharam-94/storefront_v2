from dataclasses import field
from django.forms import ImageField, ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers

from core.models import User
from favorite.models import FavoriteItem
from store.models import (
    Cart,
    CartItem,
    Category,
    Customer,
    CustomerImage,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Review,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "phone_number"]
        read_only_fields = ["id"]


class CustomerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerImage
        fields = ["image"]

    def create(self, validated_data):
        customer_id = self.context["customer_id"]
        # update image instead of always creating a new one
        # because the relation is One-to-One fields
        instance, _ = CustomerImage.objects.update_or_create(
            customer_id=customer_id, defaults=validated_data
        )
        return instance


# list/detail Customer


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, customer):
        request = self.context.get("request")
        if hasattr(customer, "image") and customer.image:
            url = customer.image.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    class Meta:
        model = Customer
        fields = [
            "id",
            "user",
            "image",
            "birth_date",
            "location",
            "second_phone_number",
        ]


class UpdateCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)
    # to upload an image as a nested related field use serializers.ImageField()
    image_file = serializers.ImageField(write_only=True)

    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, customer):
        request = self.context.get("request")  # DRF automatically passes this
        if hasattr(customer, "image") and customer.image:
            url = customer.image.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    class Meta:
        model = Customer
        fields = [
            "user",
            "image",
            "image_file",
            "birth_date",
            "location",
            "second_phone_number",
        ]

    def update(self, instance, validated_data):
        print(f'validated_data::{validated_data["image_file"]}')

        # Extract nested fields
        user_data = validated_data.pop("user", None)
        image_data = validated_data.pop("image_file", None)

        # Update user
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        # Update or create customer image
        if image_data:
            customer_image_instance, created = CustomerImage.objects.get_or_create(
                customer=instance
            )
            customer_image_instance.image = image_data
            customer_image_instance.save()

        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    images = serializers.SerializerMethodField(
        read_only=True,
    )

    image_file = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
    )

    def get_images(self, product: Product):
        request = self.context["request"]
        return [
            request.build_absolute_uri(img.image.url) for img in product.images.all()
        ]

    def get_image_file(self, product: Product):
        return ProductImageSerializer(product.images, many=True).data

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "description",
            "price",
            "inventory",
            "images",
            "image_file",
        ]

    def create(self, validated_data):
        images = validated_data.pop("image_file", [])
        # create the product
        created_product = Product.objects.create(**validated_data)

        # create the product_image instance
        for image in images:
            ProductImage.objects.create(product=created_product, image=image)

        return created_product

    def update(self, instance, validated_data):
        images = validated_data.pop("image_file", [])
        instance.images.all().delete()

        for image in images:
            ProductImage.objects.create(product=instance, image=image)

        return super().update(instance, validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["rate", "description", "product", "customer"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        product = Product.objects.get(pk=product_id)
        customer = Customer.objects.get(user_id=self.context["request"].user.id)

        # check if review already exists
        review = Review.objects.filter(customer=customer, product=product).first()

        if review:
            # update the rate & description
            review.rate = validated_data["rate"]
            review.description = validated_data.get("description", review.description)
            review.save()
            return review
        else:
            # create new review
            return Review.objects.create(
                customer=customer,
                product=product,
                rate=validated_data["rate"],
                description=validated_data.get("description", ""),
            )


class ToggleFavoriteProductSerializer(serializers.Serializer):
    # get the product_id from context because we already got it from url path
    # product_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Product.objects.all(),
    #     write_only=True,
    #     )

    def save(self, **kwargs):
        user = self.context["request"].user
        product_id = self.context["product"].id

        # check if the user has favorite the product before then delete the FavoriteItem
        product_content_type = ContentType.objects.get_for_model(Product)
        favorite_item = FavoriteItem.objects.filter(
            content_type=product_content_type, object_id=product_id, user_id=user.id
        ).first()

        if favorite_item:
            favorite_item.delete()
            return None
        else:
            favorite_item = FavoriteItem.objects.create(
                user=user, content_type=product_content_type, object_id=product_id
            )

            return favorite_item


class FavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(source="content_object", read_only=True)

    class Meta:
        model = FavoriteItem
        fields = ["product"]


class CustomerFavoriteProductSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()

    def get_favorites(self, customer: Customer):
        content_type = ContentType.objects.get_for_model(Product)
        print(f"user_id:: {customer.user.id}")
        favorite_item = FavoriteItem.objects.select_related("content_type").filter(
            content_type=content_type, user_id=customer.user.id
        )
        return FavoriteProductSerializer(
            favorite_item, context=self.context, many=True
        ).data

    class Meta:
        model = Customer
        fields = ["favorites"]


from rest_framework.exceptions import ValidationError

class CartItemSerializer(serializers.ModelSerializer):
    product_price = serializers.SerializerMethodField(read_only=True)
    items_price = serializers.SerializerMethodField(read_only=True)
    cart_id = serializers.SerializerMethodField(read_only=True)

    def get_product_price(self, cartitem: CartItem):
        return cartitem.product.price 

    def get_items_price(self, cartitem: CartItem):
        return cartitem.product.price * cartitem.quantity

    def get_cart_id(self, cartitem: CartItem):
        return cartitem.cart.id

    class Meta:
        model = CartItem
        fields = ["cart_id", "product", "quantity", "product_price", "items_price"]
        read_only_fields = ["product_price", "items_price"]

    def create(self, validated_data):
        request = self.context["request"]

        # check if the customer is authenticated or not
        customer = None
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()

        # check if the user has a cart
        cart = Cart.objects.filter(customer=customer).first() if customer else None

        if not cart:
            cart_id = request.session.get("cart_id")
            if cart_id:
                try:
                    cart = Cart.objects.get(pk=cart_id)
                except Cart.DoesNotExist:
                    cart = None

            if not cart:
                cart = Cart.objects.create(customer=customer)
                if not customer:  # only track in session for anon users
                    request.session["cart_id"] = str(cart.id)
                    request.session.set_expiry(60 * 60 * 24 * 7)

        # check if the cart already has this product
        product = validated_data['product']
        new_quantity = validated_data.get('quantity', 1)

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            # check inventory before increasing
            if cart_item.quantity + new_quantity > product.inventory:
                raise ValidationError(
                    {"detail": f"Only {product.inventory} items available in stock."}
                )
            cart_item.quantity += new_quantity
            cart_item.save()
        else:
            # check inventory before creating
            if new_quantity > product.inventory:
                raise ValidationError(
                    {"detail": f"Only {product.inventory} items available in stock."}
                )
            cart_item = CartItem.objects.create(cart=cart, **validated_data)

        return cart_item



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, cart: Cart):
        return sum(item.product.price for item in cart.cart_items.all())

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]
        read_only_fields = ["id", "items", "total_price"]


class OrderItemSerializer(serializers.Serializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "current_price",
        ]
        read_only_fields = ["id", "quantity", "current_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, order: Order):
        return sum(item.price for item in order.items.all())

    class Meta:
        model = Order
        fields = ["items", "placed_at", "total_price"]
        read_only_fields = ["placed_at"]


class CreateOrderSerializer(serializers.Serializer):

    def create(self, validated_data):
        with transaction.atomic():
            customer = Customer.objects.filter(
                user=self.context["request"].user
            ).first()
            cart = Cart.objects.filter(customer=customer).first()
            if not customer:
                raise ValidationError("No customer found for this user")

            if not cart.cart_items.exists():
                raise ValidationError("Cart is empty")

            # Create the order first
            order = Order.objects.create(customer=customer)

            # validate cart_items quantity not exceeding product.inventory
            for cart_item in cart.cart_items.all():
                if cart_item.quantity > cart_item.product.inventory:
                    raise ValidationError(
                        f"Not enough quantity for {cart_item.product.title}, "
                        f"only {cart_item.product.inventory} available"
                    )

            # bulk order_items
            order_items = [
                OrderItem(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
                for cart_item in cart.cart_items.all()
            ]
            OrderItem.objects.bulk_create(order_items)

            # decrease products quantity
            for cart_item in cart.cart_items.all():
                cart_item.product.inventory -= cart_item.quantity
                cart_item.product.save()

            # deleting the cart will also deleted it's related cart_items
            cart.delete()

            return order
