from django.urls import path 
from barrowing import views 

app_name = "barrowing"

urlpatterns = [
    path("check_book_availability/", views.check_book_availability, name="check_book_availability"),
    path("delete_session/", views.delete_session, name="delete_session"),
    path("barrowing_data/<slug:slug>/", views.barrowing_data, name="barrowing_data"),

    # Ajax
   
]