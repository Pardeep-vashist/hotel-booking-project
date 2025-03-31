from django.urls import path
from .import views

urlpatterns = [
    path('admin_home/',views.admin_home_page,name="admin_panel_booking"),
]