from django.contrib import admin
from .models import CustomUser
# Register your models here.

class CustomUser_Admin(admin.ModelAdmin):
    list_display = ['f_name','l_name','email','phone_no','created_at']
    
admin.site.register(CustomUser,CustomUser_Admin)