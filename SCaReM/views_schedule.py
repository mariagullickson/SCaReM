from django.http import Http404
from django.shortcuts import render, get_object_or_404
import models
from datetime import datetime


def view_by_camp(request):
    if 'camp_id' not in request.GET:
        raise Http404("You must select a camp")
    camp_id = int(request.GET['camp_id'])
    reservations = models.Reservation.objects.filter(camp__id__exact=camp_id) \
                                             .filter(start_time__gt=datetime.now()) \
                                             .order_by('start_time', 'end_time')
    camp = get_object_or_404(models.Camp, pk=camp_id)
    data = {
        'reservations': group_reservations_by_day(reservations),
        'camp_name': camp.name,
        }
    return render(request, 'schedule/bycamp.html', data)

def group_reservations_by_day(reservations):
    """This method takes in a list of reservation objects that are assumed
    to be sorted by date and time.  It returns a list of pairs, each
    representation one day's worth of reservations.  The first item in
    the pair is the day.  The second item is a list of reservations
    that occur on that day.

    """
    reservation_days = []
    last_day = ''
    last_day_reservations = []
    for reservation in reservations:
        this_day = reservation.start_time.date()
        if this_day != last_day:
            if last_day_reservations:
                reservation_days.append((last_day, last_day_reservations))
            last_day = this_day
            last_day_reservations = []
        last_day_reservations.append(reservation)
    if last_day_reservations:
        reservation_days.append((last_day, last_day_reservations))
        
    return reservation_days
