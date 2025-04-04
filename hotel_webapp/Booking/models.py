from django.db import models
from hotel.models import Room_Category
from payment_gateway.models import Payment
# Create your models here.

class Meal_Type(models.Model):

    room_only = "room_only"
    hb = "hb"
    fb = "fb"

    MEAL_CHOICES = [
        (room_only,'Room Only'),
        (hb,'Half Board'),
        (fb,'Full Board')
    ]

    meal_category = models.CharField(choices=MEAL_CHOICES,max_length=225,unique=True)
    meal_price = models.DecimalField(max_digits = 8,decimal_places=2,default="room_only")

    def __str__(self):
        return self.meal_category


class Booking(models.Model):
    category = models.ForeignKey('hotel.Room_Category',null=True,on_delete = models.SET_NULL)

    check_in = models.DateField()
    check_out = models.DateField()

    meal_type = models.ForeignKey(Meal_Type,null=True,on_delete=models.SET_NULL)
    no_of_rooms = models.IntegerField(default=1)
    no_of_days = models.IntegerField(null=True,blank=True,default=1)
    price_per_night = models.FloatField(default=0.0)
    room_choices = [
        (1,1),
        (2,2),
        (3,3),
        (4,4),
    ]
    no_of_room = models.IntegerField(choices=room_choices,default=1)

    # room_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    payment = models.ForeignKey('payment_gateway.Payment',on_delete=models.SET_NULL,null=True,blank=True,related_name='booking_payment')

    def save(self,*args,**kwargs):
        self.no_of_days = (self.check_out-self.check_in).days
        # print(self.no_of_days)
        super().save(*args,**kwargs)

class discountPercentages(models.Model):
    Time_Period = models.CharField(max_length=10)
    Discount_Percentage = models.FloatField()