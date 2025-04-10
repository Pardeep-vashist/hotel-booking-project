from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models.functions import Coalesce
from django.db.models import Count,Q,Sum
from datetime import datetime
from hotel.models import Room_Category
from Booking.models import Booking
import json
# Create your views here.


def check_avalability_of_room(request):
    try:
        if request.method == 'POST':
            booking_data = json.loads(request.body)
            # print("check_avalability_of_room is working", booking_data)

            if (booking_data.get('check_in') != '' and booking_data.get('check_out') != '') and booking_data.get('check_in') < booking_data.get('check_out') and booking_data.get('room_type') != '':
                check_in = datetime.strptime(
                    booking_data.get('check_in'), "%Y-%m-%d").date()
                check_out = datetime.strptime(
                    booking_data.get('check_out'), "%Y-%m-%d").date()

                available_rooms = get_avaliable_rooms(room_type_id=booking_data.get('room_type'),
                                                      check_in=check_in, check_out=check_out)

                if available_rooms > 0:
                    avalibility_status = {
                        'avalibility_status': 'Rooms are avaliable',
                    }
                    return JsonResponse(avalibility_status)
                else:
                    avalibility_status = {
                        'avalibility_status': 'Rooms are not avaliable',
                    }
                    return JsonResponse(avalibility_status)
            else:
                # print("*************************")
                avalibility_status = {
                    'avalibility_status': 'Please provide correct Details',
                }
                print(avalibility_status)
                return JsonResponse(avalibility_status)

    except Exception as e:
        avalibility_status = {
            'avalibility_status': f'ERROR IN AVAILABILITY STATUS:{e}',
        }
        return JsonResponse(avalibility_status)


def get_avaliable_rooms(room_type_id, check_in, check_out):
    # print("get_avaliable_rooms is working", room_type_id, check_in, check_out)
    try:
        
        # booked_count = Booking.objects.filter(Q(category=room_type_id)&Q(check_in=check_in))
        # print(f"booked_count = {booked_count.aggregate(Sum('no_of_rooms'))}")
        booked_count = Booking.objects.filter(
            category=room_type_id,
            check_in__lt=check_out,
            check_out__gt=check_in).aggregate(sum=Coalesce(Sum('no_of_room'),0))
        print(Booking.objects.filter(category=room_type_id,check_in__lt=check_out,check_out__gt=check_in))
        total_rooms = Room_Category.objects.get(id=room_type_id).total_rooms
        available_rooms = total_rooms-booked_count['sum']
        print(f"available_rooms ={available_rooms}")
        return available_rooms
    except Exception as e:
        print("In Function GET AVALIABLE ROOM ERROR:", e)
