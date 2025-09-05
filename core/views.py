from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import utils
from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView

from core.serializers import CustomSetUsernameSerializer

# override the default djoser view to send a custom response
#  with success message and the new_phone_number field


class CustomUserViewSet(UserViewSet):
    @action(detail=False, methods=['patch'], serializer_class=CustomSetUsernameSerializer)
    def set_phone_number(self, request, *args, **kwargs):
        response = super().set_username(request, *args, **kwargs)
        if response.status_code >= status.HTTP_200_OK:
            print(f'request data:: {request.data}')
            return Response(
                {"message": "Phone number updated successfully.",
                    "phone_number": request.data['new_phone_number'],
                 },
                status=status.HTTP_200_OK
            )
        return response


# implement create token view (login)
class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )

# implement delete token view (logout)


class CustomTokenDestroyView(TokenDestroyView):
    # we don't need @action because we extend normal ApiView not ViewSet
    def post(self, request):
        # Call original logout logic
        super().post(request)
        # Always return JSON message
        return Response(
            {"message": "Token deleted successfully"},
            status=status.HTTP_200_OK
        )
