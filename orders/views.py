from email.policy import HTTP
from telnetlib import STATUS
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
import razorpay 
from store.models import Product
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 



razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
def place_order(request):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    amount = ((total + tax)*100)




    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.pincode = form.cleaned_data['pincode']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") 
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount,currency = "INR",payment_capture='0'))
 
            # order id of newly created order.
            razorpay_order_id = razorpay_order['id']
            order.provider_order_id = razorpay_order_id
            order.save()
            callback_url = 'order_complete/'
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'amount' : amount,
                'callback_url':callback_url,
                'razorpay_order_id':razorpay_order_id,
                "razorpay_key": settings.RAZOR_KEY_ID,
            }

            return render(request, 'orders/review.html', context)
        else:
            return HttpResponse(form.errors)
    else:
        return redirect('checkout')




   
@csrf_exempt
def order_complete(request):
    if request.method == "POST":
        try:
            # get the required parameters from post request.

            provider_order_id = request.POST.get("razorpay_order_id", "")
            payment_id = request.POST.get('razorpay_payment_id', '')
            order = Order.objects.get(user=request.user, is_ordered=False, provider_order_id=provider_order_id)
            # Store transaction details inside Payment model
            payment = Payment(
                    user = request.user,
                    payment_id = payment_id,
                    payment_method = "online method",
                    amount_paid = order.order_total,
                    payment_status = 'Complete'
                )
            payment.save()
            order.payment = payment
            order.is_ordered = True
            order.save()
            # Move the cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                 orderproduct = OrderProduct()
                 orderproduct.order_id = order.id
                 orderproduct.payment = payment
                 orderproduct.user_id = request.user.id
                 orderproduct.product_id = item.product_id
                 orderproduct.quantity = item.quantity
                 orderproduct.product_price = item.product.price
                 orderproduct.ordered = True
                 orderproduct.save()
                 cart_item = CartItem.objects.get(id=item.id)
                 product_variation = cart_item.variations.all()
                 orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                 orderproduct.variations.set(product_variation)
                 orderproduct.save()

                 # Reduce the quantity of the sold products                 
                 product = Product.objects.get(id=item.product_id)
                 product.stock -= item.quantity
                 product.save()
            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order recieved email to customer
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_recieved_email.html', {
                    'user': request.user,
                    'order': order,
                })
            email_from = settings.EMAIL_HOST_USER
            to_email = order.email
            send_mail( mail_subject, message, email_from,[to_email])

            payments = Payment.objects.get(payment_id=payment_id)

            ordered_products = OrderProduct.objects.filter(order_id=order.id)
            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payments,
                    'subtotal': subtotal,
        }
            return render(request, 'orders/order_complete.html',context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')
