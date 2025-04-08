from django.contrib import admin
from .models import Amenity,Room_Category,Room_Category_Images
# # Register your models here.

class Amenity_Admin(admin.ModelAdmin):
    list_display = ['name','icons','is_available','availability_start','availability_end']
    
class Room_Category_Admin(admin.ModelAdmin):
    list_display = ['category','room_size','room_desc','price','total_rooms','get_amenities','gallery_images']
    
    def get_amenities(self,obj):
        return [i for i in obj.amenities.all()]
    
    def gallery_images(self,obj):
        return [i for i in obj.room_category_images_set.all()]
admin.site.register(Amenity,Amenity_Admin)
admin.site.register(Room_Category,Room_Category_Admin)
admin.site.register(Room_Category_Images)
