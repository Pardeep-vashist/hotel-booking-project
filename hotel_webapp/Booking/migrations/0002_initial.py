# Generated by Django 5.1.4 on 2025-03-29 01:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Booking', '0001_initial'),
        ('payment_gateway', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_payment', to='payment_gateway.payment'),
        ),
        migrations.AddField(
            model_name='booking',
            name='meal_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Booking.meal_type'),
        ),
    ]
