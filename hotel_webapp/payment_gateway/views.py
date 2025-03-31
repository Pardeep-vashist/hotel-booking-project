from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from custom_user.models import CustomUser
from Booking.models import discountPercentages,Booking,Meal_Type
from Booking.views import dynamic_price
from hotel.models import Room_Category
import base64
import uuid
import json
import hashlib
import requests

def generate_tran_id():
    # To generate a unique order number
    uuid_part = str(uuid.uuid4()).split('-')[0].upper()
    now = datetime.now().strftime("%y%m%d")
    return f"TRX{now}{uuid_part}"

def generate_checksum(data,salt_key,salt_index):
    "To Generate checksum"
    checksum_str = data + '/pg/v1/pay' + salt_key
    checksum = hashlib.sha256(checksum_str.encode()).hexdigest() + '###' + salt_index
    return checksum

@csrf_exempt
def initiate_payment(request):
    if request.method == "POST":
        # print("Payment Initialized")
        user_data = json.loads(request.body.decode('utf-8'))
        amount= int(float(user_data['amount']))
        cate = user_data['room_type']

        transaction_id = generate_tran_id()
        # callback_url = request.build_absolute_uri(reverse('payment/callback',args=[transaction_id]))
        callback_url = request.build_absolute_uri(reverse('payment_gateway:callback',args=[transaction_id]))
        
        print(user_data)

        payload = {
            'merchantId': settings.PHONEPE_MERCHANT_ID,
            "merchantTransactionId":transaction_id,
            'merchantUserId':"MUID123",
            "amount": int(amount)*100, # In paisa
            "redirectUrl": callback_url,
            "redirectMode":"POST",
            "callbackUrl":callback_url,
            "mobileNumber":"9999999999",
            "paymentInstrument":{
                "type":"PAY_PAGE"
            },
        }

        data = base64.b64encode(json.dumps(payload).encode()).decode()
        checksum = generate_checksum(data,settings.PHONEPE_MERCHANT_KEY,settings.SALT_INDEX)
        final_payload = {
            "request" : data,
        }

        headers = {
            "access-control-allow-origin" : "*",
            'Content-Type' : 'application/json',
            'X-VERIFY':checksum
        }

        # all_categories = Room_Category.ROOM_CATEGORIES

        # print("ALL CATEGORIES",all_categories)

        try:
            amounts = dynamic_price(room_category=user_data['room_type'],meal_category=user_data['meal_type'],
            check_in_date=user_data['checkIn'],check_out_date=user_data['checkOut'],no_of_rooms=user_data['totalrooms'])

            # print("Amounts Returned",amounts,amounts['total_amount']==int(user_data['amount']))
            if amounts['total_amount']==int(user_data['amount']):
                # print("GreatGreatGreatGreatGreatGreatGreatGreatGreatGreatGreatGreatGreat")
                pass
            else:
                print("PAYMENT MISMATCH")
                return JsonResponse({'error':"Payment amount mismatch",'reload':True})

        except Exception as e:
            print("Error In Dynamic Price Calculation:",e)

        try:
            response = requests.post(settings.PHONEPE_INITIATE_PAYMENT_URL+'/pg/v1/pay',headers=headers,json=final_payload)
            data = response.json()
            print(data)
            if data['success']:
                url = data['data']['instrumentResponse']['redirectInfo']['url']
                url_map = {'url':url,'reload':False}

                try:
                    user = CustomUser(f_name = user_data['fname'],l_name=user_data['lname'],email=user_data['email'],
                                phone_no = user_data['phone_no'])
                    user.save()

                    payment_data = Payment()
                    payment_data.user = user
                    payment_data.transaction_id = transaction_id
                    payment_data.amount_paid = amounts['total_amount']
                    payment_data.payment_date = datetime.today()
                    payment_data.save()

                    try:
                        request.session.cycle_key() 
                        request.session['booking_data']={
                            'transaction_id':transaction_id,
                            'user_id':user.id,
                            'room_type':user_data['room_type'],
                            'meal_type':user_data['meal_type'],
                            'check_in':user_data['checkIn'],
                            'check_out':user_data['checkOut'],
                            'totalrooms':user_data['totalrooms'],
                            'amount':amounts['total_amount'],
                            "room_price_per_night_offered":amounts['room_price'],
                        }
                        request.session.modified = True
                        request.session.save()
                        print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr*5",request.session['booking_data'])

                    except Exception in e:
                        print("Error in creating Session:",e)
                        
                except Exception as e:
                    print("Exception in Booking or Payment",e)

                return JsonResponse(url_map)
            else:
                return redirect(cate)
        except Exception as e:
            return redirect(reverse(cate))


@csrf_exempt
def payment_callback(request,transaction_id):
    # print("#######################",request)
    if request.method != 'POST':
        # logger.error("Invalid request method: %s",request.method)
        return redirect('/')

    try:
        data = request.POST.dict()
        # print(data)
        payment_data = Payment.objects.get(transaction_id=data['transactionId'])
        payment_data.payment_status = data['code'] 
        payment_data.payment_date = datetime.now().date()
        payment_data.save()

        if data.get('checksum') and data.get('code') == 'PAYMENT_SUCCESS':
            try:
                if payment_data.payment_status == 'PAYMENT_SUCCESS':
                    # Create a booking only for successful payments
                    try:
                        room_data = request.session['booking_data']
                        print("Room Data:",room_data)
                        if not room_data:
                            redirect('/')
                        # room_type_mapping = {
                        #         'BSN': Room_Category.BUSINESS,
                        #         'DLX': Room_Category.TWIN_BED,
                        #         'SUITE': Room_Category.SUITE
                        #     }
                        
                        # room_type_category = Room_Category.objects.get(id=room_data['room_type'])     
                        
                        # # if room_type_category:
                        # #     room_type = Room_Category.objects.get(category=room_type_category)
                        # if room_type_category:
                        #     print("Invalid room type:", room_data['room_type'])
                        #     try:
                        #         room_type = Room_Category.objects.get(category=room_type_category)
                        #     except Room_Category.DoesNotExist:
                        #         print("Room category does not exist:", room_type_category)
                        #         return redirect('/')  # Or handle the error

                        #     return redirect('/')  # Or handle the error appropriately
                        try:
                            room_type_category = Room_Category.objects.get(id=room_data['room_type'])
                        except Room_Category.DoesNotExist:
                            print("Room category does not exist:", room_type_category)
                            return redirect('/')  # Or handle the error
                            
                        if room_data['meal_type']:
                            meal = Meal_Type.objects.get(id=room_data['meal_type'])
                        # if room_data['meal_type']:
                        #     if room_data['meal_type'] == "room_only":
                        #         meal = Meal_Type.objects.get()
                        #     elif room_data['meal_type'] == "hb":
                        #         meal = Meal_Type.objects.get(meal_category=Meal_Type.hb)
                        #     elif room_data['meal_type'] == "fb":
                        #         meal = Meal_Type.objects.get(meal_category=Meal_Type.fb)
                                
                    except Exception as e:
                        print("Problem in getting Booking Session Data:",e)
        
                    try:
                        booking = Booking()
                        booking.category=room_type_category
                        booking.check_in=datetime.strptime(room_data['check_in'],"%Y-%m-%d").date()
                        booking.check_out=datetime.strptime(room_data['check_out'],"%Y-%m-%d").date()
                        booking.meal_type=meal
                        booking.no_of_room=room_data['totalrooms']
                        booking.room_price_per_night_offered = room_data["room_price_per_night_offered"]
                        booking.room_price=room_data['amount']
                        booking.payment=payment_data
                        booking.save()
                        payment_data.booking = booking
                        payment_data.save()
                        # print(type(booking.category),type(booking.check_in),type(booking.check_out),type(booking.meal_type),type(booking.no_of_room),type(booking.room_price),type(booking.payment))
                    except Exception as e:
                        print("Error in New Booking:",e)
                        
            except Exception as e:
                print("Exception in Booking",e)


            user_booking_data = Payment.objects.get(transaction_id=transaction_id)
            print("************************************")
            print(user_booking_data)
            context={'user_booking_detail':booking,
            'payment_detail':payment_data
            }
            response = render(request,'payment_gateway/success.html',context)
            request.session.clear()
            return response
        else:
            request.session.clear()
            return render(request,'failed.html')
    except Exception as e:
        print("Error in callback",e)
        request.session.clear()
        return render(request,"failed.html")


# function for calculating amount based on parameters selectedd by user like Room Category,
# Meal Category Check In & Check Out Dates.It Will validate the amount that will be paid by user.


