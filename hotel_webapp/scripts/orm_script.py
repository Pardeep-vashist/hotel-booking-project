# from accommodation.models import Room,Booking,Room_Category,Payment,Booking
from accommodation.models import Payment,Booking
from datetime import datetime
from django.db.models import Q
from django.db import connection

# def run():
#     room_category = Room_Category.objects.all()
#     today_date = datetime.now().date()
#     category_wise_room = {}

#     for i in range(0,len(room_category)):
#         category = room_category[i]
#         booking_data = Booking.objects.filter(Q(check_out=today_date)&Q(category=category))

#         for booking_entry in booking_data:
#             category=booking_entry.category.category
#             room_update=booking_entry.no_of_room
#             no_of_room = category_wise_room.get(category)

#             if no_of_room is None:
#                 no_of_room = 0

#             category_wise_room.update({booking_entry.category.category:no_of_room+room_update})

#     print(category_wise_room)

#     # category_wise_room = {'STD': 3, 'DLX': 1, 'STE': 1}

#     for key,value in category_wise_room.items():
#         category_obj = Room_Category.objects.filter(category=key).first()
#         room_availability = category_obj.total_rooms-value
#         category_obj.available_rooms = room_availability
#         print(category_obj.available_rooms)
#         category_obj.save()
        
#     # print(Room_Category.objects)

def run():
    # user_booking_data =  Payment.objects.filter(payment_status='PAYMENT_SUCCESS').select_related('booking').filter(transaction_id='TRX2502289F2039C8')

    user_booking_data = Payment.objects.get(transaction_id='TRX2502289F2039C8')
    print(user_booking_data.booking.check_out)



