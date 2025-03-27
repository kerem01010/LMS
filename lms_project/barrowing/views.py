from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string


from library.models import Library,  Barrowing, LibraryGallery, LibraryFeatures

from datetime import datetime
from decimal import Decimal


from django.contrib import messages



def check_book_availability(request):

        try:
            checkin_date = datetime.strptime(request.POST['checkin'], '%Y-%m-%d').date()
            checkout_date = datetime.strptime(request.POST['checkout'], '%Y-%m-%d').date()

            # Get the reservation for the specified  type and date range
            reservations = Barrowing.objects.filter(
                check_in_date__lte=checkout_date,
                check_out_date__gte=checkin_date
            )

            # Calculate the number of days the book will be reserved
            reservation_duration = (checkout_date - checkin_date).days

            # Check if the book is available for the entire duration
            if reservations.exists():
                messages.error(request, 'Sorry, the book is not available for the specified dates.')
            elif reservation_duration > 14:
                messages.error(request, 'Sorry, a book can only be reserved for a maximum of 14 days.')
            else:
                # Create a new reservation
                reservation = Barrowing(
                    
                    checkin_date=checkin_date,
                    checkout_date=checkout_date,
                    user=request.user  # Assuming you have a user associated with the reservation
                    
                )
                reservation.save()
                messages.success(request, 'Your reservation has been confirmed.')

            return redirect('barrowing:check_book_availability')  # Redirect back to the same page
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('barrowing:check_book_availability')


def barrowing_data(request, slug):
    library = Library.objects.get( slug=slug)
    context = {
        "library":library,
    }
    return render(request, "barrowing/barrowing_data.html", context)

def delete_session(request):
    request.session.pop('selection_data_obj', None)
    return redirect(request.META.get("HTTP_REFERER"))


def delete_selection(request):
    library_id = str(request.GET['id'])
    if 'selection_data_obj' in request.session:
        if library_id in request.session['selection_data_obj']:
            selection_data = request.session['selection_data_obj']
            del request.session['selection_data_obj'][library_id]
            request.session['selection_data_obj'] = selection_data


    total = 0
    total_days = 0
    
     
    checkin = "" 
    checkout = "" 
    children = 0 
    library = None

    if 'selection_data_obj' in request.session:
        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['library_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]

            
            library = Library.objects.get(id=id)

            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            days = total_days
        
        
    
    
    
