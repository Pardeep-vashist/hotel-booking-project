from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail,EmailMessage,get_connection
from django.template.loader import get_template
from weasyprint import HTML
from django.template import context
from django.template.loader import render_to_string      
from io import BytesIO
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from custom_user.models import CustomUser
from Booking.models import discountPercentages,Booking,Meal_Type,Invoice
from Booking.views import dynamic_price
from hotel.models import Room_Category
import base64
import uuid
import json
import hashlib
import requests
import os

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
        print("vvvvvvvvvvvvvvv",request.POST.get('user_data'))
        user_data = json.loads(request.body.decode('utf-8'))
        print("fffffffffffff",user_data)
        
        if user_data['meal_type']=="":
            user_data['meal_type']=None
            
        if user_data['fname']!="" and user_data['lname']!="" and user_data['phone_no']!="" and user_data['email']!="" and user_data['checkIn']!="" and user_data['checkOut']!="" and user_data['room_type']!="" and user_data['totalrooms']!="" and  user_data['allAdults']!="" and user_data['meal_type']!="" and user_data['amount']!="":
            def check_for_space(user_data):
                for key,item in user_data.items():
                    if str(item).isspace():
                        return True
                    
            # inner function to check for spaces        
            contain_space = check_for_space(user_data)
            if contain_space:
                return JsonResponse({'error':"contain space"})
                  
            amount= int(float(user_data['amount']))
            cate = user_data['room_type']
            print(user_data)
            transaction_id = generate_tran_id()
            # callback_url = request.build_absolute_uri(reverse('payment/callback',args=[transaction_id]))
            callback_url = request.build_absolute_uri(reverse('payment_gateway:callback',args=[transaction_id]))
            
            

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
                for key,value in amounts.items():
                    if value is None:
                        return JsonResponse({'error':"DYNAMIC PRICE AMOUNTS CONTAIN NONE VALUES",'reload':True})        

                if int(user_data['allAdults'])<1:
                    return JsonResponse({'error':"Adults should be greater ",'reload':True})

                # print("dsfffdfdf",int(amounts['total_amount'])!=int(user_data['amount']))
                if int(amounts['total_amount'])!=int(user_data['amount']):
                    print("dddddddddPAYMENT MISMATCH")
                    return JsonResponse({'error':"Payment amount mismatch",'reload':True})
                
                # return JsonResponse({'error':"Payment amount mismatch",'reload':True})

            except Exception as e:
                print(f"Error In Dynamic Price we got:{e}")
                return JsonResponse({"error":f"Error In Dynamic Price we got:{e}"})

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
                                "user_email":user.email,
                                'room_type':user_data['room_type'],
                                'meal_type':user_data['meal_type'],
                                'check_in':user_data['checkIn'],
                                'check_out':user_data['checkOut'],
                                'totalrooms':user_data['totalrooms'],
                                'amount':amounts['total_amount'],
                                "room_price_per_night_offered":amounts['each_room_price'],
                            }
                            request.session.modified = True
                            request.session.save()
                            # print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr*5",request.session['booking_data'])

                        except Exception in e:
                            print("Error in creating Session:",e)
                            
                    except Exception as e:
                        print("Exception in Booking or Payment",e)

                    return JsonResponse(url_map)
                else:
                    return redirect(cate)
            except Exception as e:
                return redirect(reverse(cate))
        else:
            return JsonResponse({"error":"user_data is empty"})
        
def send_email_to_hotel(invoice_pdf):
    try:
        subject = "New Room Booking"
        message = f"Thank YOU"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_HOST_USER]
        email = EmailMessage(subject,message,from_email,recipient_list)
        email.attach_file(invoice_pdf)
        # email.send()
        # send_mail(subject,message,from_email,recipient_list,fail_silently=True)
    except Exception as e:
        print(f"ERROR IN SENDING EMAIL TO HOTEL:{e}")
    
def send_email_to_user(user_email,invoice_pdf):
    try:
        connection = get_connection()
        connection.open()
        subject = "Your Room Booking is Confirmed!"
        message = f"Hello, your booking is confirmed! Details:"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        email = EmailMessage(subject,message,from_email,recipient_list,connection=connection)
        email.attach_file(invoice_pdf)
        # email.send()
        # send_mail(subject,message,from_email,recipient_list,fail_silently=True)
        connection.close()
    except Exception as e:
        print(f"ERROR IN SENDING EMAIL TO USER:{e}")
    
def generateInvoice(new_booking,transaction_id):
    try:
        template = get_template('payment_gateway/invoice.html')
        print(template)
        
        user_payment_detail = Payment.objects.get(transaction_id=transaction_id)
        user_detail=user_payment_detail.user
        user_booking_detail = user_payment_detail.booking
        print(user_booking_detail.meal_type)
        
        fname = user_payment_detail.user.f_name
        lname = user_payment_detail.user.l_name
        category = user_booking_detail.category
        check_in = user_booking_detail.check_in
        check_out = user_booking_detail.check_out
        no_of_room = user_booking_detail.no_of_room
        no_of_days = user_booking_detail.no_of_days
        price_per_night = user_booking_detail.price_per_night
        grand_total = user_booking_detail.payment.amount_paid
        meal = user_booking_detail.meal_type
        meal_price = user_booking_detail.meal_type.meal_price
        total_meal_price = meal_price

        # grand_total = int(total_room_price) + int(total_meal_price)
        booking_data = {'fname':fname,'lname':lname,'category':category,'check_in':check_in,'check_out':check_out,
        'no_of_days':no_of_days,'no_of_room':no_of_room,'meal':meal,'meal_price':meal_price,
        'grand_total':grand_total,'price_per_night':price_per_night,'total_room_price':no_of_days*price_per_night*no_of_room
         }
        # print(booking_data)
        
        html_invoice = template.render(booking_data)
        pdf_file = BytesIO()
        HTML(string=html_invoice).write_pdf(pdf_file)
        file_path = os.path.join(settings.BASE_DIR,'invoices\\')
        
        filename = file_path+f'invoice_{new_booking.id}.pdf'
        print(filename)
        with open(filename, 'wb+') as pdf:
            pdf.write(pdf_file.getvalue())

        return filename
    except Exception as e:
        print(f"ERROR IN INVOICE:{e}")

@csrf_exempt
def payment_callback(request,transaction_id):
    if request.method != 'POST':
        return redirect('/')

    try:
        data = request.POST.dict()
        payment_data = Payment.objects.get(transaction_id=data['transactionId'])
        payment_data.payment_status = data['code'] 
        payment_data.payment_date = datetime.now().date()
        payment_data.save()

        if data.get('checksum') and data.get('code') == 'PAYMENT_SUCCESS':

            if payment_data.payment_status == 'PAYMENT_SUCCESS':
                # Create a booking only for successful payments
                room_data = request.session['booking_data']
                print("Room Data:",room_data)
                if not room_data:
                    redirect('/')

                room_type_category = Room_Category.objects.get(id=room_data['room_type'])
                print("frffffffffffffffffffffff")   
                if room_data['meal_type']!=None:
                    meal = Meal_Type.objects.get(id=room_data['meal_type'])
                else:
                    meal=None
                print("frffffffffffffffffffffff")
                booking = Booking()
                booking.category=room_type_category
                booking.check_in=datetime.strptime(room_data['check_in'],"%Y-%m-%d").date()
                booking.check_out=datetime.strptime(room_data['check_out'],"%Y-%m-%d").date()
                booking.meal_type=meal
                booking.no_of_room=room_data['totalrooms']
                booking.price_per_night = room_data["room_price_per_night_offered"]
                booking.payment=payment_data
                booking.save()
                payment_data.booking = booking
                payment_data.save()
                print("##########################",booking)
                user_booking_data = Payment.objects.get(transaction_id=transaction_id)
                context={'user_booking_detail':booking,
                'payment_detail':payment_data,
                'total_room_price':booking.no_of_days*booking.price_per_night*booking.no_of_room,
                }

                response = render(request,'payment_gateway/success.html',context)
            
                invoice_pdf = generateInvoice(booking,transaction_id)
                booking_invoice = Invoice.objects.create(booking=booking,invoice=invoice_pdf)
                user_email=room_data['user_email']
                send_email_to_user(user_email,invoice_pdf)
                send_email_to_hotel(invoice_pdf)
                request.session.clear()
                return response
        else:
            data = request.POST.dict()
            print("PAYMENT FAILED OR PENDING",data)
            payment_data.payment_status = data['code'] 
            request.session.clear()
            response = render(request,'payment_gateway/failed.html')
            return response
    except Exception as e:
        data = request.POST.dict()
        print("PAYMENT FAILED OR PENDING",data)
        payment_data.payment_status = data['code']
        print("Error in callback",e)
        request.session.clear()
        return render(request,"payment_gateway/failed.html")


# function for calculating amount based on parameters selectedd by user like Room Category,
# Meal Category Check In & Check Out Dates.It Will validate the amount that will be paid by user.


