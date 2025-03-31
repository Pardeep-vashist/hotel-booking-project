from django.urls import path
from . import views

app_name='payment_gateway'

urlpatterns = [
    path('booking',views.initiate_payment,name="book_room"),
    path('callback/<str:transaction_id>/',views.payment_callback,name='callback'),
]