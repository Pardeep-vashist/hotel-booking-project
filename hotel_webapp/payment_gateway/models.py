from django.db import models
from custom_user.models import CustomUser
# from Booking.models import Booking
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    booking = models.ForeignKey('Booking.Booking',on_delete=models.SET_NULL,null=True,blank=True,related_name="payment_after_booking")
    payment_status = models.CharField(max_length=128,default="PAYMENT INITIATED")
    transaction_id = models.CharField(max_length=128,blank=True,null=True)
    amount_paid = models.IntegerField(default=0)
    currency = models.CharField(max_length=15,default="INR")
    payment_date = models.DateField(null=True,blank=True)

    def __str__(self):
        return str(self.transaction_id)