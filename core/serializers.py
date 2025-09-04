from djoser.serializers import UserCreatePasswordRetypeSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token

import phonenumbers

from core.models import User


# create user serializer/ response after creating a user
class CustomUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer):
    phone_number = serializers.CharField()
    token = serializers.SerializerMethodField()

    def get_token(self, user: User):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    def validate_phone_number(self, value):
        try:
            # parse phone numbers with Egypt as the default value
            parsed_number = phonenumbers.parse(value, 'EG')

            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number.")

            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format.")

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = ['id', 'token', 'phone_number', 'email', 'first_name',
                  'last_name', 'password']
        


# get user serializer
class CustomUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        fields = ['id', 'phone_number', 'first_name',
                  'last_name', 'email', 'token']
