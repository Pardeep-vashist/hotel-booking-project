from django.urls import path
from . import views

urlpatterns = [
    path('room', views.show_booking_page, name=""),
    path('get-room-price', views.on_date_change_price, name=""),
    path('meal', views.meal_type),
    path("decrease_room_price", views.decrease_room_price),
    path("room_price_hotel_room", views.increase_price),
]
