from django.contrib import admin
from django.utils.html import format_html
from .models import Booking,Meal_Type,discountPercentages,Invoice
# Register your models here.

class Meal_Admin(admin.ModelAdmin):
    list_display = ['meal_category','meal_price']
    
class Booking_Admin(admin.ModelAdmin):
    list_display = ['category','check_in','check_out','get_meal','no_of_days','price_per_night','no_of_room','payment']
    
    def get_meal(self,obj):
        return obj.meal_type.meal_category
    
    # def invoice_of_booking(self,obj):
    #     return format_html('<a href="{}" target="_blank">{}</a>',obj.invoice_after_booking.invoice.url,obj.invoice_after_booking.invoice)
    
    # invoice_of_booking.allow_tags = True
    
class Discount_Percentage_Admin(admin.ModelAdmin):
    list_display = ('Time_Period','Discount_Percentage')
    
admin.site.register(Meal_Type,Meal_Admin)
admin.site.register(discountPercentages,Discount_Percentage_Admin)
admin.site.register(Booking,Booking_Admin)
admin.site.register(Invoice)