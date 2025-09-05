from djoser.serializers import UserCreatePasswordRetypeSerializer, TokenSerializer, UserSerializer, SetUsernameSerializer
from rest_framework import  serializers
from rest_framework.authtoken.models import Token

import phonenumbers

from core.models import User


def check_phone_number(value):
    try:
        # parse phone numbers with Egypt as the default value
        parsed_number = phonenumbers.parse(value, 'EG')
        if not phonenumbers.is_valid_number(parsed_number):
            raise serializers.ValidationError("Invalid phone number.")
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise serializers.ValidationError("Invalid phone number format.")
    
class TokenMixin(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, user: User):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

# create user serializer/ response after creating a user
class CustomUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer, TokenMixin):
    phone_number = serializers.CharField()
 
    def validate_phone_number(self, value):
        return check_phone_number(value)

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = ['id', 'token', 'phone_number', 'email', 'first_name',
                  'last_name', 'password']


# get user serializer
class CustomUserSerializer(UserSerializer, TokenMixin):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ['id', 'phone_number', 'first_name',
                  'last_name', 'email', 'token']
        
# User to return the login response
class CustomTokenSerializer(TokenSerializer):
    user = CustomUserSerializer()
    class Meta(TokenSerializer.Meta):
        fields = ['user']


# change phone_field
class CustomSetUsernameSerializer(SetUsernameSerializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta(SetUsernameSerializer.Meta):
        model = User
        fields = ['phone_number', 'password']

    # for validation of the new phone number to work
    # you have to define validate_new_phone_number in validate_phone_number
    def validate_new_phone_number(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "This phone number is already used.")
        new_phone = check_phone_number(value)
        return new_phone
    






