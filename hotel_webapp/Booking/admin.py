from django.contrib import admin
from .models import Booking,Meal_Type,discountPercentages
# Register your models here.

admin.site.register(Meal_Type)
admin.site.register(discountPercentages)
admin.site.register(Booking)