# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CheckoutSessionAPIView.as_view(), name='create_checkout_session'),
    path('success/', views.SuccessAPIView.as_view(), name='success'),
    path('cancel/', views.CancelAPIView.as_view(), name='cancel'),
    path('webhook/', views.StripeWebhookAPIView.as_view(), name='stripe_webhook'), # Add this line
]
