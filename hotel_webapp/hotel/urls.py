from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('',views.home_page,name=""),
    path('gallery/',views.gallery,name="gallery"),
    path('contact/',views.contact_us,name="contact"),
    path('about-us/',TemplateView.as_view(template_name="about-us.html"),name="about-us"),
]

