from dataclasses import field
from django.forms import ImageField
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from core.models import User
from favorite.models import FavoriteItem
from store.models import (
    Category,
    Customer,
    CustomerImage,
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
        for image in images:
            instance.images.all().delete()
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
        customer = Customer.objects.get(
            user_id=self.context["request"].user.id)

        # check if review already exists
        review = Review.objects.filter(
            customer=customer, product=product).first()

        if review:
            # update the rate & description
            review.rate = validated_data["rate"]
            review.description = validated_data.get(
                "description", review.description)
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
        user = self.context['request'].user
        product_id = self.context['product'].id

        # check if the user has favorite the product before then delete the FavoriteItem
        product_content_type = ContentType.objects.get_for_model(Product)
        favorite_item = FavoriteItem.objects.filter(
            content_type=product_content_type, object_id=product_id, user_id=user.id).first()

        if favorite_item:
            favorite_item.delete()
            return None
        else:
            favorite_item = FavoriteItem.objects.create(
                user=user, content_type=product_content_type, object_id=product_id)

            return favorite_item
