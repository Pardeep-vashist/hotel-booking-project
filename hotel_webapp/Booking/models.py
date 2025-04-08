from django.db import models
from hotel.models import Room_Category
from payment_gateway.models import Payment
# Create your models here.

class Meal_Type(models.Model):
    meal_category = models.CharField(max_length=225,unique=True)
    meal_price = models.DecimalField(max_digits = 8,decimal_places=2,default="room_only")

    def __str__(self):
        return self.meal_category


class Booking(models.Model):
    category = models.ForeignKey('hotel.Room_Category',null=True,on_delete = models.SET_NULL)

    check_in = models.DateField()
    check_out = models.DateField()

    meal_type = models.ForeignKey(Meal_Type,null=True,on_delete=models.SET_NULL)
    no_of_days = models.IntegerField(null=True,blank=True,default=1)
    price_per_night = models.FloatField(default=0.0)
    room_choices = [
        (1,1),
        (2,2),
        (3,3),
        (4,4),
    ]
    no_of_room = models.IntegerField(default=1)
    payment = models.ForeignKey('payment_gateway.Payment',on_delete=models.SET_NULL,null=True,blank=True,related_name='booking_payment')
    
    def save(self,*args,**kwargs):
        self.no_of_days = (self.check_out-self.check_in).days
        # print(self.no_of_days)
        super().save(*args,**kwargs)

class discountPercentages(models.Model):
    Time_Period = models.CharField(max_length=10)
    Discount_Percentage = models.FloatField()
    
class Invoice(models.Model):
    booking = models.OneToOneField(Booking,null=True,on_delete=models.SET_NULL,related_name="invoice_after_booking")
    invoice = models.FileField(upload_to='invoices/')
    created = models.DateTimeField(auto_now_add=True)