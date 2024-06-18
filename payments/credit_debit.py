from rest_framework.response import Response
from rest_framework import status
from .models import Payment

class CardPayment:

    @staticmethod
    def process_payment(data):
        try:
            # Credit/Debit card payment processing logic here
            # Replace the code below with your actual credit/debit card payment processing logic
            # Here we are just printing the information to demonstrate the process
            print("Processing payment with Credit/Debit card...")
            print("Payment data:", data)
            
            # Saving payment data to the database
            payment = Payment.objects.create(
                name=data.get('name'),
                company=data.get('company'),
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                country=data.get('country'),
                postal_code=data.get('postal_code'),
                phone_number=data.get('phone_number'),
                payment_method=data.get('payment_method'),
                card_holder_name=data.get('card_holder_name'),
                card_number=data.get('card_number'),
                expiry_date=data.get('expiry_date'),
                cvc=data.get('cvc'),
                review=data.get('review'),
                ship_to=data.get('ship_to')
            )
            payment.save()

            return True, "Payment successfully processed with Credit/Debit card."
        except Exception as e:
            return False, str(e)
