from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from Rooms.views import get_avaliable_rooms
from hotel.models import Room_Category, Room_Category_Images
from .models import discountPercentages, Meal_Type
from datetime import datetime
import urllib.parse
import json
from decimal import Decimal


def show_booking_page(request):
    try:
        requested_url = urllib.parse.unquote(request.build_absolute_uri())
        path = requested_url[32:]
        path = json.loads(path)
        print(path)
        room_type = Room_Category.objects.get(id=path.get('room_type', None))
        # print("**************", room_type)
        check_in = path.get('check_in', None)
        check_out = path.get('check_out', None)

        if room_type != None and check_in != None and check_out != None:
            available_rooms = get_avaliable_rooms(
                path.get('room_type'), check_in, check_out)
            if available_rooms > 0:
                room_category_images = room_type.room_category_images_set.all()[
                    :4]
                print("**************", room_category_images)
                amenities_related_to_room_type = room_type.amenities.all()

                all_amounts = dynamic_price(room_category=path.get('room_type'), meal_category=1,
                                            check_in_date=check_in, check_out_date=check_out, no_of_rooms=1)

                all_meal_types = Meal_Type.objects.all()
                context = {
                    'room_category_images': room_category_images,
                    'amenities': amenities_related_to_room_type,
                    'room_name': room_type.category,
                    'room_price': all_amounts['room_price'],
                    'meal_price': all_amounts['meal_category_price'],
                    'total_amount': all_amounts['total_amount'],
                    'room_type_id': room_type.id,
                    'all_meal_types': all_meal_types,
                }
                return render(request, 'Booking/booking.html', context)
            else:
                return redirect('hotel/home')

        else:
            return redirect('hotel/home')

    except Exception as e:
        print("ERROR IN SHOW BOOKING PAGE:", e)


def increase_price(request):
    data = json.loads(request.body.decode('utf-8'))
    price = data['hotel_room_price']
    check_in_date = datetime.strptime(data['check_in_date'], "%Y-%m-%d")

    amounts = dynamic_price(room_category=data['form_room_type'],
                            meal_category=None, check_in_date=data['check_in_date'],
                            check_out_date=data['check_out_date'], no_of_rooms=1)

    price = Decimal(price) + Decimal(amounts['room_price'])
    print(f"AMOUNTS:{amounts}")
    price_dic = {
        'price': price,
    }

    return JsonResponse(price_dic)


def decrease_room_price(request):
    data = json.loads(request.body.decode('utf-8'))
    price = data['hotel_room_price']
    print(data)
    amounts = amounts = dynamic_price(room_category=data['form_room_type'],
                                      meal_category=None, check_in_date=data['check_in_date'],
                                      check_out_date=data['check_out_date'], no_of_rooms=1)

    price = Decimal(price) - Decimal(amounts['room_price'])
    price_dic = {
        'price': price,
    }
    return JsonResponse(price_dic)


def on_date_change_price(request):

    user_data = json.loads(request.body.decode('utf-8'))
    print(f"user data:{user_data}")
    amounts = dynamic_price(room_category=user_data['roomType'],
                            meal_category=user_data['meal_type'], check_in_date=user_data['checkIn'],
                            check_out_date=user_data['checkOut'], no_of_rooms=user_data['no_of_room'])

    return JsonResponse(amounts)


def meal_type(request):
    data = json.loads(request.body.decode('utf-8'))
    print(data['meal_type'])
    amounts = dynamic_price(room_category=None,
                                      meal_category=data['meal_type'], check_in_date=data['check_in_date'],
                                      check_out_date=data['check_out_date'], no_of_rooms=None)
    print(" meal_type meal_type meal_type meal_type",amounts)
    return JsonResponse({'data': amounts['meal_category_price']})


def dynamic_price(room_category, meal_category, check_in_date, check_out_date, no_of_rooms):
    try:
        # print(f"data passed for changing dates,{room_category}i,{meal_category},{check_in_date}, {check_out_date},{no_of_rooms}")
        if check_in_date != None and check_out_date != None:
            room_check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d")
            room_check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d")

            if room_check_in_date < room_check_out_date:
                no_of_days = (room_check_out_date-room_check_in_date).days
                discounts = discountPercentages.objects.all().values()
                print("****************discounts",discounts is None)
                if len(discounts)!=0:        
                    for i in range(len(discounts)):
                        discounts_offered = discounts[i]['Time_Period'].split("to")
                        applied_offer = [int(i) for i in discounts_offered]
                        applied_offer.sort()
                        today = datetime.now().date()
                        in_advance_days = int(
                            (room_check_in_date.date() - today).days)

                        if in_advance_days >= applied_offer[0] and in_advance_days <= applied_offer[1]:
                            offer_got = discounts[i]['Discount_Percentage']
                            print("OFFER GOT:", type(offer_got))
                            break
                else:
                    offer_got = 0
                    
            if room_category != None:
                room_base_price = float(
                    Room_Category.objects.get(id=int(room_category)).price)
                print("ROOM VASE PRICE", room_base_price)
                discount_amount = (offer_got/100)*room_base_price
                price_after_discount = room_base_price-discount_amount
                calculated_room_price = round(
                    price_after_discount*float(no_of_days)*float(no_of_rooms))
            else:
                calculated_room_price = 0
    
            if meal_category != None:
                try:
                    meal_category_price = float(Meal_Type.objects.get(
                        id=meal_category).meal_price)
                except ObjectDoesNotExist:
                    meal_category_price = 0
                    print("Meal Not Avaliable")
            else:
                meal_category_price = 0
                
            if type(meal_category_price)!=str:
                total_amount = int(calculated_room_price + meal_category_price)
            else:
                total_amount = int(calculated_room_price)
            calculated_amounts = {
                'room_price': calculated_room_price,
                'meal_category_price': meal_category_price,
                'total_amount': total_amount,
                'each_room_price': price_after_discount,
            }
            print(calculated_amounts)

            return calculated_amounts
    except Exception as e:
        calculated_amounts = {
            'room_price':None,
            'meal_category_price': None,
            'total_amount': None,
            'each_room_price': None,
        }
        print("ERROR IN DYNAMIC PRICE CALCULATION:", e)
        return calculated_amounts
