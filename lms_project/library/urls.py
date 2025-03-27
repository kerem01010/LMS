from django.urls import path 
from library import views 

app_name = "library"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug:slug>/", views.library_detail, name="detail"),
    path("checkout/<barrowing_id>/", views.checkout, name="checkout"),
    path("invoice/<barrowing_id>/", views.invoice, name="invoice"),
    path('all-books/', views.all_books, name='all_books'),
    
path('search/', views.search_books, name='search_books'),

    # Payment API
    path('api/checkout-session/<barrowing_id>/', views.create_checkout_session, name='api_checkout_session'),
    path('success/<barrowing_id>/', views.payment_success, name='success'),
    path('failed/<barrowing_id>/', views.payment_failed, name='failed'),
]