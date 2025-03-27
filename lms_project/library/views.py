from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .utils import sort_books, binary_search  # Importing utility functions


from library.models import Coupon, CouponUsers, Library,  Barrowing, LibraryGallery, LibraryFeatures, Notification, Bookmark, Review

from datetime import datetime
from decimal import Decimal
import stripe
import json


def search_books(request):
    query = request.GET.get('query', '')
    found_book = None
    if query:
        books = list(Library.objects.all())  # Tüm kitapları veritabanından al
        sorted_books = sort_books(books)  # Kitapları sırala
        found_book = binary_search(sorted_books, query)  # İkili arama yap
    context = {'book': found_book, 'query': query}  # Sorguyu temsil etmek için context'e ekleyin
    return render(request, 'library/search.html', context)

def all_books(request):
    # Retrieve all books from the database
    all_books = Library.objects.all()
    # Pass the books to the template for rendering
    return render(request, 'library/all_books.html', {'books': all_books})

def index(request):
    library = Library.objects.filter(status="Live")
    context = {
        "library":library
    }
    return render(request, "library/index.html", context)


def library_detail(request, slug):
    library = Library.objects.get(slug=slug)
    try:
        reviews = Review.objects.filter(user=request.user, library=library)
    except:
        reviews = None
    all_reviews = Review.objects.filter(library=library, active=True)
    
    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, library=library)
    else:
        bookmark = None
    context = {
        "library":library,
        "bookmark":bookmark,
        "reviews":reviews,
        "all_reviews":all_reviews,
    }
    return render(request, "library/library_detail.html", context)




def checkout(request, barrowing_id):
    barrowing = Barrowing.objects.get(barrowing_id=barrowing_id)

    if barrowing.payment_status == "paid":
        messages.success(request, "This order has been paid for!")
        return redirect("/")
    else:
        barrowing.payment_status = "processing"
        barrowing.save()


    # Coupon
    now = timezone.now()
    if request.method == "POST":
        # Get code entered in the input field
        code = request.POST.get('code')
        print("code ======", code)
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
            if coupon in barrowing.coupons.all():
                messages.warning(request, "Coupon Already Activated")
                return redirect("library:checkout", barrowing.barrowing_id)
            else:
                CouponUsers.objects.create(
                    barrowing=barrowing,
                    coupon=coupon,
                    full_name=barrowing.full_name,
                    email=barrowing.email,
                    mobile=barrowing.phone,
                )

                if coupon.type == "Percentage":
                    discount = barrowing.total * coupon.discount / 100
                else:
                    discount = coupon.discount

                barrowing.coupons.add(coupon)
                barrowing.total -= discount
                barrowing.saved += discount
                barrowing.save()

                
                messages.success(request, "Coupon Found and Activated")
                return redirect("library:checkout", barrowing.barrowing_id)
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon Not Found")
            return redirect("library:checkout", barrowing.barrowing_id)
    
    context = {
        "barrowing":barrowing,  
        "stripe_publishable_key":settings.STRIPE_PUBLIC_KEY,
        "flutter_publick_key":settings.FLUTTERWAVE_PUBLIC,
        "website_address":settings.WEBSITE_ADDRESS,
    }
    return render(request, "library/checkout.html", context)


@csrf_exempt
def create_checkout_session(request, barrowing_id):
    request_data = json.loads(request.body)
    barrowing = get_object_or_404(Barrowing, barrowing_id=barrowing_id)

    stripe.api_key = settings.STRIPE_PRIVATE_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = barrowing.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': barrowing.full_name,
                    },
                    'unit_amount': int(barrowing.total * 100),
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('library:success', args=[barrowing.barrowing_id])) + "?session_id={CHECKOUT_SESSION_ID}&success_id="+barrowing.success_id+'&barrowing_total='+str(barrowing.total),
        cancel_url=request.build_absolute_uri(reverse('library:failed', args=[barrowing.barrowing_id]))+ "?session_id={CHECKOUT_SESSION_ID}",
    )

    barrowing.payment_status = "processing"
    barrowing.stripe_payment_intent = checkout_session['id']
    barrowing.save()

    print("checkout_session ==============", checkout_session)
    return JsonResponse({'sessionId': checkout_session.id})


def payment_success(request, barrowing_id):
    success_id = request.GET.get('success_id')
    barrowing_total = request.GET.get('barrowing_total')

    if success_id and barrowing_total: 
        success_id = success_id.rstrip('/')
        barrowing_total = barrowing_total.rstrip('/')
        
        barrowing = Barrowing.objects.get(barrowing_id=barrowing_id, success_id=success_id)
        
        # Payment Verification
        if barrowing.total == Decimal(barrowing_total):
            if barrowing.payment_status == "processing": #processing #paid
                barrowing.payment_status = "paid"
                barrowing.save()

                noti = Notification.objects.create(barrowing=barrowing,type="Barrowing Confirmed",)
                if request.user.is_authenticated:
                    noti.user = request.user
                    noti.save()
                else:
                    noti = None
                    noti.save()

                # Delete the  Sessions
                if 'selection_data_obj' in request.session:
                    del request.session['selection_data_obj']
               
                subject = f"Barrowing Completed - Invoice & Summary - ID: #{barrowing.barrowing_id}"
              
                    
            elif barrowing.payment_status == "paid":
                messages.success(request, f'Your barrowing has been completed.')
                return redirect("/")
            else:
                messages.success(request, 'Opps... Internal Server Error; please try again later')
                return redirect("/")
                
        else:
            messages.error(request, "Error: Payment Manipulation Detected, This payment have been cancelled")
            barrowing.payment_status = "failed"
            barrowing.save()
            return redirect("/")
    else:
        messages.error(request, "Error: Payment Manipulation Detected, This payment have been cancelled")
        barrowing = Barrowing.objects.get(barrowing_id=barrowing_id, success_id=success_id)
        barrowing.payment_status = "failed"
        barrowing.save()
        return redirect("/")
    
    context = {
        "barrowing": barrowing, 
    }
    return render(request, "library/payment_success.html", context) 


def payment_failed(request, barrowing_id):
    barrowing = Barrowing.objects.get(barrowing_id=barrowing_id)
    barrowing.payment_status = "failed"
    barrowing.save()
                
    context = {
        "barrowing": barrowing, 
    }
    return render(request, "library/payment_failed.html", context) 


def invoice(request, barrowing_id):
    barrowing = Barrowing.objects.get(barrowing_id=barrowing_id)

    context = {
        "barrowing":barrowing,  
        
    }
    return render(request, "library/invoice.html", context)

