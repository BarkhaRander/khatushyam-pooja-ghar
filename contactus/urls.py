from django.urls import path
from . import views

urlpatterns = [
    path('contact_us/', views.contact_us, name='contact_us'),
    path('contact/', views.contact, name='contact'),
]