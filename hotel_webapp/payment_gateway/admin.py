from django.contrib import admin
from .models import Payment
# Register your models here.

class Payment_Admin(admin.ModelAdmin):
    list_display = ['user','booking','payment_status','transaction_id','amount_paid','currency','payment_date']
    
admin.site.register(Payment,Payment_Admin)