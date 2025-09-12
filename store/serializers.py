from django.forms import ImageField
from rest_framework import serializers

from core.models import User
from store.models import Customer, CustomerImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id']


class CustomerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerImage
        fields = ['image']

    def create(self, validated_data):
        customer_id = self.context['customer_id']
        # update image instead of always creating a new one 
        # because the relation is One-to-One fields
        instance, _ = CustomerImage.objects.update_or_create(
            customer_id=customer_id,
            defaults=validated_data
        )
        return instance

# list/detail Customer
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField(
        read_only = True
    )

    def get_image(self, customer):
        request = self.context.get('request')  # DRF automatically passes this
        if hasattr(customer, 'image') and customer.image:
            url = customer.image.image.url
            return request.build_absolute_uri(url) if request else url
        return None
    class Meta:
        model = Customer
        fields = ['id', 'user', 'image', 'birth_date', 'location',
                  'second_phone_number',
                  ]



class UpdateCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)
    # to upload an image as a nested related field use serializers.ImageField()
    image_file = serializers.ImageField(write_only=True)

    image = serializers.SerializerMethodField(
        read_only = True
    )

    def get_image(self, customer):
        request = self.context.get('request')  # DRF automatically passes this
        if hasattr(customer, 'image') and customer.image:
            url = customer.image.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    class Meta:
        model = Customer
        fields = ['user', 'image', 'image_file', 'birth_date', 'location', 'second_phone_number']

    

    def update(self, instance, validated_data):
        print(f'validated_data::{validated_data["image_file"]}')

        # Extract nested fields
        user_data = validated_data.pop('user', None)
        image_data = validated_data.pop('image_file', None)

        # Update user
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        # Update or create customer image
        if image_data:
            customer_image_instance, created = CustomerImage.objects.get_or_create(customer=instance)
            customer_image_instance.image = image_data
            customer_image_instance.save()
    
        return super().update(instance, validated_data)
