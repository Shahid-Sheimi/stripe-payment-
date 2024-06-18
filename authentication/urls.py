from django.urls import path
from .views import SignUpView, SignInView, ActivateView, ForgotPasswordView, ResetPasswordView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('sign-up/', SignUpView.as_view(), name='sign_up'),
    path('sign-in/', SignInView.as_view(), name='sign_in'),
    path('activate/<str:uidb64>/<str:token>/', ActivateView.as_view(), name='activate'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset_password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset password'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
]
