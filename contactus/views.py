from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from accounts.models import Account
from .models import ContactUs
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


# Create your views here.
def contact(request):
    user = Account.objects.get(username__exact=request.user.username)
    context={
        'user': user
    }

    return render(request,'accounts/contactus.html',context)

def contact_us(request):
    current_user = request.user
    if request.method == 'POST':
        subject = request.POST['subject']
        contact = ContactUs.objects.create(user=current_user,s = subject)
        contact.save()

        # Send order recieved email to customer
        mail_subject = 'Query from customer'
        message = render_to_string('accounts/customer_query_email.html', {
                    'user': request.user,
                    's' : subject
        })
        email_from = request.user.email
        to_email = settings.EMAIL_HOST_USER
        send_mail( mail_subject, message, email_from,[to_email])
        messages.success(request, 'Mail Sent')
        return render(request,'accounts/contactus.html')
    # return HttpResponse(request.method)
