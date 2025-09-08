from rest_framework import serializers

from core.models import User
from store.models import Customer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id']


# list/detail Customer
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'birth_date', 'location',
                  'second_phone_number',
                  ]


# update customer
class UpdateCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Customer
        fields = ['user', 'birth_date', 'second_phone_number']


    def update(self, instance, validated_data):
        # get the user object from validated data the remove it
        user_data = validated_data.pop('user', None)

        # update the user
        if user_data:
            user = instance.user
            # iterate over user_data dictionary items to update the user instance with right values
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # update the customer profile
        instance = super().update(instance, validated_data)

        return instance

    

