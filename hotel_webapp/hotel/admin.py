from django.contrib import admin
from .models import Amenity,Room_Category,Room_Category_Images
# # Register your models here.

admin.site.register(Amenity)
admin.site.register(Room_Category)
admin.site.register(Room_Category_Images)
