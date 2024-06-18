# views.py
from rest_framework import status, viewsets
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from authentication.backends import EmailBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
from .models import User

User = get_user_model()

# Swagger Schema for SignUpView
signup_view_post_schema = {
    "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
    "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email Address"),
    "pass1": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
    "pass2": openapi.Schema(type=openapi.TYPE_STRING, description="Confirm Password"),
}

signup_view_responses = {
    200: openapi.Response("Success", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
            'link': openapi.Schema(type=openapi.TYPE_STRING, description="Activation Link")
        }
    )),
    400: openapi.Response("Bad Request", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
        }
    )),
}

# Swagger Schema for SignInView
signin_view_post_schema = {
    "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username or Email Address"),
    "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
}

signin_view_responses = {
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
}

# Swagger Schema for ActivateView
activate_view_get_parameters = [
    openapi.Parameter('uidb64', openapi.IN_PATH, type=openapi.TYPE_STRING),
    openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING),
]

activate_view_responses = {
    200: openapi.Response("Success", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message")
        }
    )),
    400: openapi.Response("Bad Request", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
        }
    )),
}

# Swagger Schema for ForgotPasswordView
forgot_password_view_post_schema = {
    "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username or Email Address"),
}

forgot_password_view_responses = {
    200: openapi.Response("Success", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
            'link': openapi.Schema(type=openapi.TYPE_STRING, description="Reset Password Link")
        }
    )),
    400: openapi.Response("Bad Request", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
        }
    )),
}

# Swagger Schema for ResetPasswordView
reset_password_view_post_schema = {
    "pass1": openapi.Schema(type=openapi.TYPE_STRING, description="New Password"),
    "pass2": openapi.Schema(type=openapi.TYPE_STRING, description="Confirm New Password"),
}

reset_password_view_responses = {
    200: openapi.Response("Success", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message")
        }
    )),
    400: openapi.Response("Bad Request", openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
        }
    )),
}

# def build_activation_email(name, activation_link):
#     subject = 'Activate Your Account'
#     body = f"Hi {name},\n\nPlease click the link below to activate your account:\n{activation_link}\n\nThank you!"
#     return subject, body

class SignUpView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'pass1', 'pass2'],
            properties=signup_view_post_schema
        ),
        responses=signup_view_responses,
        operation_summary="Register new user",
    )
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password1 = request.data.get('pass1')
        password2 = request.data.get('pass2')
        role = request.data.get('role')

        if username and email and password1 and password2:
            if password1 != password2:
                return Response(
                    status=status.HTTP_200_OK,
                    data={'error': 'Passwords do not match'}
                )
            if User.objects.filter(username=username).exists():
                return Response(
                    status=status.HTTP_200_OK,
                    data={"error": "Username already exists! Try another username."}
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    status=status.HTTP_200_OK,
                    data={"error": "Email Already Registered!"}
                )

            user = User.objects.create_user(
                username=username, email=email, password=password1)
            user.is_active = False
            if role == 'customer' or role == 'member' or role == 'admin':
                user.role = role
                
                if  role == 'admin':
                    user.is_superuser = True
                if role == 'member':
                    user.is_staff == True

            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_link = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token}))
            # subject, body = build_activation_email(user.username, activation_link)
            # send_mail(subject, body, '', [user.email])
            return Response(
                status=status.HTTP_200_OK,
                data={'message': 'Click here for Account activation. ', "link": activation_link}
            )

        else:
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data={'message': 'Account creation Failed, Please provide all details including Username, email, password, and confirm password '}
            )

class SignInView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties=signin_view_post_schema
        ),
        responses=signin_view_responses,
        operation_summary="User sign in",
    )
    def post(self, request):
        username_or_email = request.data.get('username')
        print(">>>>>>>>>>>>",username_or_email)
        password = request.data.get('password')
        user = EmailBackend.authenticate(
            self, request, username=username_or_email, password=password)
        if user is not None:
            print("LLLLLLLLLLLLLL",user)
            refresh = RefreshToken.for_user(user)
            return Response(
                status=status.HTTP_200_OK,
                data={
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user': user.email
                }
            )
        else:
            return Response(
                status=status.HTTP_200_OK,
                data={'error': 'Invalid credentials'}
            )


class ActivateView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=activate_view_get_parameters,
        responses=activate_view_responses,
        operation_summary="Activate user account",
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                status=status.HTTP_200_OK, data={'message': 'Your account has been activated successfully'}
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid activation link'}
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username'],
            properties=forgot_password_view_post_schema
        ),
        responses=forgot_password_view_responses,
        operation_summary="Request password reset",
    )
    def post(self, request):
        username = request.data.get('username')
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'error': 'User with this email does not exist'}
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONT_END_URL}/reset_password/{uid}/{token}"
        # send the link via email
        return Response(
            status=status.HTTP_200_OK,
            data={'message': 'Password reset link sent successfully', 'link': reset_link}
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=activate_view_get_parameters,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['pass1', 'pass2'],
            properties=reset_password_view_post_schema
        ),
        responses=reset_password_view_responses,
        operation_summary="Reset user password",
    )
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            password = request.data.get('pass1', None)
            password2 = request.data.get('pass2', None)
            if password != password2:
                return Response(
                    status=status.HTTP_200_OK,
                    data={'error': 'Passwords do not match'}
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if password:
                user.set_password(password)
                user.save()
                return Response(
                    data={'message': 'Password reset successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={'error': 'New password not provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                data={'error': 'Invalid password reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
