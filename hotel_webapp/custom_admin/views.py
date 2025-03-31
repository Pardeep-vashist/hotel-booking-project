from django.shortcuts import render
from django.db import connection
# Create Views Here

def admin_home_page(request):
    try:
        print("ADMIN HOME PAGE VIEW")
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Booking_booking")
            results = cursor.fetchall()
        print(results)
    except Exception as e:
        print("ADMIN HOME PAGE ERROR:",e)
    return render(request,'custom_admin/admin_home_page.html')

# def room_categories()