from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import models
from datetime import datetime

def index(request):
    return HttpResponse('Hello World!')

def create_or_edit_reservation(request, reservation_id=None):
    form_values = {
        'camps': models.Camp.objects.all(),
        'resources': models.Resource.objects.all()
    }
    errors = []

    if request.method == 'POST':
        try:
            # put together the reservation object
            reservation = models.Reservation()
            if 'reservation_id' in request.POST:
                reservation.id = request.POST['reservation_id']

            reservation.event = request.POST['event']
            if not reservation.event:
                errors.append("You must specify an Event")
            form_values['event_value'] = reservation.event

            reservation.owner = request.POST['owner']
            if not reservation.owner:
                errors.append("You must specify an Owner")
            form_values['owner_value'] = reservation.owner

            camp_id = request.POST['camp']
            if not camp_id:
                errors.append("You must specify a Camp")
            reservation.camp = get_object_or_404(models.Camp, pk=camp_id)
            form_values['camp_value'] = reservation.camp.id

            resources = [
                get_object_or_404(models.Resource, pk=resource_id)
                for resource_id in request.POST.getlist('resources')]
            if not resources:
                errors.append("You must specify at least one Resource")
            form_values['resource_values'] = [resource.id for resource in resources]

            date = request.POST['date']
            start_time = request.POST['start_time']
            end_time = request.POST['end_time']
            if not date:
                errors.append("You must specify a Date")
            if not start_time:
                errors.append("You must specify a Start Time")
            if not end_time:
                errors.append("You must specify a End Time")
            form_values['date_value'] = date
            form_values['start_time_value'] = start_time
            form_values['end_time_value'] = end_time
            if date and start_time:
                reservation.start_time = datetime.strptime(
                    "%s %s" % (date, start_time),
                    "%m/%d/%Y %I:%M%p")
            if date and end_time:
                reservation.end_time = datetime.strptime(
                    "%s %s" % (date, end_time),
                    "%m/%d/%Y %I:%M%p")
            if (reservation.start_time and reservation.end_time
                and reservation.end_time <= reservation.start_time):
                errors.append("Reservation must end after it starts")

            # TODO look for conflicts

            # save the reservation
            if not errors:
                reservation.save()
                reservation.resources = resources
                reservation.save()

                return HttpResponseRedirect('/')
        except Exception as e:
            errors.append(e.message or e.args[1])
    elif reservation_id:
        # editing an existing reservation.  load it from the database
        # and fill in form fields
        reservation = get_object_or_404(models.Reservation, pk=reservation_id)
        form_values['event_value'] = reservation.event
        form_values['owner_value'] = reservation.owner
        form_values['camp_value'] = reservation.camp.id
        form_values['resource_values'] = [
            resource.id for resource in reservation.resources.all()]
        form_values['date_value'] = reservation.start_time.strftime("%m/%d/%Y")
        form_values['start_time_value'] = reservation.start_time.strftime(
            "%I:%M%p")
        form_values['end_time_value'] = reservation.end_time.strftime("%I:%M%p")
        form_values['reservation_id'] = reservation_id

    form_values['error_messages'] = errors
    if reservation_id:
        form_values['action'] = '/reservation/edit/%s/' % reservation_id
    else:
        form_values['action'] = '/reservation/create/'

    return render(request, 'reservations/addedit.html', form_values)
            
