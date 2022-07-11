from django.shortcuts import render
from store.models import Product,ReviewRating

def home(request):
    
    products = Product.objects.all().filter(is_available=True).order_by('-averageReview1')
    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True).order_by('-rating')
    context = {
        'products' : products,
        'reviews' : reviews,
    }
    return render(request,'home.html',context)

def aboutus(request):
    return render(request,'aboutus.html')