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
            cate = "/"
            print("catecatecatecatecatecatecatecatecatecatecate",cate)
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