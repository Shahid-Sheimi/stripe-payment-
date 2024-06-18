# backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response("Success", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING, description="Access Token"),
                    'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh Token"),
                    'user': openapi.Schema(type=openapi.TYPE_STRING, description="User Email")
                }
            )),
            400: openapi.Response("Bad Request", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )),
        },
        operation_summary="Authenticate user",
    )
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if '@' in username:
                user = UserModel.objects.get(email=username)
            else:
                user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
