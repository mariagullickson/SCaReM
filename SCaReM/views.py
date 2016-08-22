from django.shortcuts import render
from models import Camp, Resource, AuditLog, Reservation
from datetime import datetime, timedelta


def index(request):
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    reservations = Reservation.objects.filter(start_time__gte=today) \
                                      .filter(end_time__lt=tomorrow) \
                                      .order_by('start_time')
    data = {
        'camps': Camp.objects.all(),
        'resources': Resource.objects.all(),
        'today': group_reservations_by_resource(reservations),
        'date': datetime.now().date(),
        }

    # check for an easter egg, show it now and clear it out
    if 'easter' in request.session:
        data['easter'] = request.session['easter']
        del request.session['easter']

    return render(request, 'index.html', data)


def log(request, year=None, month=None, day=None):
    if year:
        start_year = int(year)
        start_month = int(month) if month else 1
        start_day = int(day) if day else 1
        start_date = datetime(start_year, start_month, start_day)
        if day:
            end_date = start_date + timedelta(1)
        elif month:
            if start_month == 12:
                end_month = 1
                end_year = start_year + 1
            else:
                end_month = start_month + 1
                end_year = start_year
            end_date = datetime(end_year, end_month, 1)
        else:
            end_date = datetime(start_year + 1, 1, 1)

        logs = AuditLog.objects.filter(timestamp__gte=start_date) \
                               .filter(timestamp__lt=end_date) \
                               .order_by('timestamp')
    else:
        logs = AuditLog.objects.all().order_by('timestamp')
    data = {
        'logs': logs
    }
    return render(request, 'logs.html', data)


def group_reservations_by_resource(reservations):
    """This method takes in a list of reservation objects that are assumed
    to be sorted by time.  It returns a list of tuples, each
    representing one resources's of reservations.  The first item in
    the pair is the resource id; the second item is the resource name;
    the third item is a list of reservations that use that resource.
    Because reservations may use more than one resource, the final
    output will likely duplicate reservations in multiple lists.

    """
    reservation_resources = {}
    resource_names = {}
    for reservation in reservations:
        for resource in reservation.resources.all():
            if resource.id not in reservation_resources:
                resource_names[resource.id] = resource.name
                reservation_resources[resource.id] = []
            reservation_resources[resource.id].append(reservation)

    return [(key, resource_names[key], value)
            for key, value in reservation_resources.iteritems()]
