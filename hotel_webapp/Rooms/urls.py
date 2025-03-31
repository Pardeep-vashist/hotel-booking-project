from django.urls import path
from . import views

urlpatterns = [
    path('check_availability',views.check_avalability_of_room,name="check_availability"),
]

