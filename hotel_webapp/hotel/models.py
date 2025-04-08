from django.db import models
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.contrib import messages
from django.conf import settings
import datetime
import os
import re
# Create your models here.


class Amenity(models.Model):
    name = models.CharField(max_length=128, unique=True)
    icons = models.ImageField(upload_to="images", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    availability_start = models.DateTimeField(null=True, blank=True)
    availability_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Room_Category(models.Model):
    category = models.CharField(max_length=25, unique=True)
    room_size = models.CharField(max_length=128, null=True, blank=True)
    room_desc = models.CharField(max_length=128, default="This is a Best Room")
    amenities = models.ManyToManyField(Amenity, blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    total_rooms = models.IntegerField(null=True, blank=True)
    # available_rooms = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.category


class Room_Category_Images(models.Model):
    category = models.ForeignKey(
        Room_Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='media')

    def __str__(self):
        return str(self.image)

