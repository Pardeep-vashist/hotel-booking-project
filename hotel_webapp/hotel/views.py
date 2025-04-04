from django.shortcuts import render
from .models import Room_Category,Amenity
# Create your views here.

def home_page(request):
    all_room_types = Room_Category.objects.all()

    context = {
        'all_room_types':all_room_types,
    }

    return render(request,'hotel/index.html',context)

def contact_us(request):
    return render(request,"hotel/contact_us.html")

def gallery(request):
    return render(request,'hotel/gallery.html')