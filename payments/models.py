from django.db import models
from authentication.models import User
import datetime

# Create your models here.

class Transaction(models.Model):
    txn_id = models.CharField(max_length=40, unique=True, blank= True, null=True)
    transaction_date = models.DateTimeField()
    amount = models.FloatField()
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    STATUS_CHOICES = [
        ("Received", "Received"),
        ("Refund", "Refund"),
    ] 
    amount_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Received')

    refund_to = models.CharField(max_length=25, null= True, blank=True)
    reason_of_refund = models.CharField(max_length=50, null=True, blank= True)
    cancelled_on = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount_refund = models.FloatField(null=True,blank=True)

    def __str__(self):
        return f"Transaction ID {self.txn_id}"