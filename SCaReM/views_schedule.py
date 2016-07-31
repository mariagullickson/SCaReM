from django.http import Http404
from django.shortcuts import render, get_object_or_404
from models import Reservation, Camp, Resource
import settings
import views
from datetime import datetime


def view_by_camp(request):
    if 'camp_id' not in request.GET or not request.GET['camp_id']:
        return views.index(request, ["You must select a camp"])
    camp_id = int(request.GET['camp_id'])
    reservations = Reservation.objects.filter(camp__id__exact=camp_id) \
                                      .filter(start_time__gt=datetime.now()) \
                                      .order_by('start_time', 'end_time')
    camp = get_object_or_404(Camp, pk=camp_id)
    data = {
        'reservations': group_reservations_by_day(reservations),
        'camp_name': camp.name,
        }
    return render(request, 'schedule/bycamp.html', data)

def view_by_resource(request):
    if 'resource_id' not in request.GET or not request.GET['resource_id']:
        return views.index(request, ["You must select a resource"])
    resource_id = int(request.GET['resource_id'])
    resource = get_object_or_404(Resource, pk=resource_id)
    reservations = Reservation.objects.filter(resources__id__exact=resource_id) \
                                      .filter(start_time__gt=datetime.now()) \
                                      .order_by('start_time', 'end_time')
    data = {
        'reservations': group_reservations_by_day(reservations),
        'resource_name': resource.name,
        }
    return render(request, 'schedule/byresource.html', data)

def view_by_date(request):
    # start date is required, end date is optional.  if end date is not
    # specified, use the start date
    if 'start_date' not in request.GET or not request.GET['start_date']:
        return views.index(request, ["You must select a date"])
    start_time = datetime.strptime(request.GET['start_date'] + " 12 : 00 AM",
                                   settings.DATETIME_FORMAT)
    use_end_date = 'end_date' in request.GET and request.GET['end_date']
    if use_end_date:
        end_time = datetime.strptime(request.GET['end_date'] + " 11 : 59 pm",
                                     settings.DATETIME_FORMAT)
    else:
        end_time = datetime.strptime(request.GET['start_date'] + " 11 : 59 pm",
                                     settings.DATETIME_FORMAT)

    reservations = Reservation.objects.filter(start_time__gte=start_time) \
                                      .filter(end_time__lte=end_time) \
                                      .order_by('start_time', 'end_time')
    data = {
        'reservations': group_reservations_by_day(reservations),
        'start_date': start_time,
        'end_date': end_time if use_end_date else None,
        }
    return render(request, 'schedule/bydate.html', data)

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
