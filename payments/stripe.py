# stripe.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CardInformationSerializer
from django.conf import settings
import stripe
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

class StripePayment(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CardInformationSerializer

    @swagger_auto_schema(
        request_body=CardInformationSerializer,
        responses={
            200: openapi.Response("Success", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Payment status"),
                    'payment_intent': openapi.Schema(type=openapi.TYPE_STRING, description="Payment intent ID")
                }
            )),
            400: openapi.Response("Bad Request", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )),
        },
        operation_summary="Process card payment",
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                intent = stripe.PaymentIntent.create(
                    amount=int(data['amount'] * 100),  # Amount in cents
                    currency='usd',
                    payment_method_types=['card'],
                )
                intent.payment_method = data['payment_method']
                intent.confirm()
                return Response({
                    'status': 'Payment processed successfully.',
                    'payment_intent': intent.id
                }, status=status.HTTP_200_OK)
            except stripe.error.CardError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'your-stripe-webhook-secret'
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        # Handle successful payment intent
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        # Handle failed payment intent

    return JsonResponse({'status': 'success'})
