# payments/views.py
import stripe
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone

from drf_yasg import openapi
from datetime import datetime
from .models import Transaction
stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET

class CheckoutSessionAPIView(APIView):
    # print("helolo   jjjjjjjjjjjj")
    permission_classes = [IsAuthenticated]  # Allow unrestricted access
    print("helolo   jjjjjjjjjjjj")

    @swagger_auto_schema(
        operation_description="Create a new Checkout Session",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'url': openapi.Schema(type=openapi.TYPE_STRING)})},
    )
    def post(self, request):
        # Create a new Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': '3D Modelling',
                        },
                        'unit_amount': 1000,  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cancel')),
        )

        return Response({'url': session.url})

class SuccessAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unrestricted access

    @swagger_auto_schema(
        operation_description="Get success message",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})},
    )
    def get(self, request):
        return Response({'message': 'Success'}, status=status.HTTP_200_OK)

class CancelAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unrestricted access

    @swagger_auto_schema(
        operation_description="Get cancel message",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})},
    )
    def get(self, request):
        return Response({'message': 'Canceled'}, status=status.HTTP_200_OK)

class StripeWebhookAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unrestricted access

    @swagger_auto_schema(
        operation_description="Handle Stripe webhook events",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={})},
    )
    def post(self, request):
        sig_header = request.headers.get('Stripe-Signature', None)
        payload = request.body
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, 
                sig_header=sig_header, 
                secret=webhook_secret
            )
        except ValueError as e:
            # Handle ValueError
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Handle SignatureVerificationError
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle payment intent events
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Process successful payment intent
            self.handle_successful_payment_intent(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Process failed payment intent
            self.handle_failed_payment_intent(payment_intent)

        return Response(status=status.HTTP_200_OK)

    def handle_successful_payment_intent(self, payment_intent):
        payment_intent_id = payment_intent['id']
        amount_received = payment_intent['amount_received']

       

        # Process further as needed

        # transaction_created = datetime.fromtimestamp(int(payment_intent['created']))
        transaction_created = timezone.make_aware(datetime.fromtimestamp(int(payment_intent['created'])))

        updated, transaction = Transaction.objects.update_or_create(
            txn_id = payment_intent_id,
            
            defaults={
                'transaction_date' : transaction_created ,
                'amount' : amount_received/100,
                'payment_method' :payment_intent['payment_method_types'][0] ,
            }
        )

    def handle_failed_payment_intent(self, payment_intent):
        payment_intent_id = payment_intent['id']
        failure_reason = payment_intent['last_payment_error']['message']
        # Process further as needed
        print("Payment intent failed. ID:", payment_intent_id)
        print("Failure reason:", failure_reason)
