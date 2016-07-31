from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
import models
from datetime import datetime, timedelta
import json
import settings

def index(request):
    data = {
        'camps': models.Camp.objects.all(),
        'resources': models.Resource.objects.all(),
        }
    return render(request, 'index.html', data)

def create_or_edit_reservation(request, reservation_id=None):
    resources = models.Resource.objects.all()
    tag_resources = {}
    for resource in resources:
        for tag in resource.tags.all():
            if tag.id not in tag_resources:
                tag_resources[tag.id] = []
            tag_resources[tag.id].append(resource.id)
    
    form_values = {
        'camps': models.Camp.objects.all(),
        'resources': models.Resource.objects.all(),
        'tags': models.Tag.objects.all(),
        'tag_resources': json.dumps(tag_resources),
    }
    errors = []

    if request.method == 'POST':
        try:
            # put together the reservation object
            reservation = models.Reservation()
            if 'reservation_id' in request.POST and request.POST['reservation_id']:
                reservation.id = int(request.POST['reservation_id'])

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
            else:
                reservation.camp = get_object_or_404(models.Camp, pk=camp_id)
                form_values['camp_value'] = reservation.camp.id

            resource_ids = [int(x) for x in request.POST.getlist('resources')]
            resources = [
                get_object_or_404(models.Resource, pk=resource_id)
                for resource_id in resource_ids]
            if not resources:
                errors.append("You must specify at least one Resource")
            form_values['resource_values'] = [
                resource.id for resource in resources]

            date = request.POST['date']
            if date:
                try:
                    test = datetime.strptime(date, settings.DATE_FORMAT)
                    form_values['date_value'] = date
                except:
                    errors.append("Invalid Date.  Should be formatted as MM/DD/YYYY")
                    date = None
            else:
                errors.append("You must specify a Date")

            start_time = request.POST['start_time']
            if start_time:
                try:
                    test = datetime.strptime(start_time, settings.TIME_FORMAT)
                    form_values['start_time_value'] = start_time
                except:
                    errors.append("Invalid Start Time.  Should be formatted as HH : MM {am/pm}.")
                    start_time = None
            else:
                errors.append("You must specify a Start Time")

            end_time = request.POST['end_time']
            if end_time:
                try:
                    test = datetime.strptime(end_time, settings.TIME_FORMAT)
                    form_values['end_time_value'] = end_time
                except:
                    errors.append("Invalid End Time.  Should be formatted as HH : MM {am/pm}.")
                    end_time = None
            else:
                errors.append("You must specify a End Time")

            if date and start_time:
                reservation.start_time = datetime.strptime(
                    "%s %s" % (date, start_time),
                    settings.DATETIME_FORMAT)
            if date and end_time:
                reservation.end_time = datetime.strptime(
                    "%s %s" % (date, end_time),
                    settings.DATETIME_FORMAT)
            if (reservation.start_time and reservation.end_time
                and reservation.end_time <= reservation.start_time):
                errors.append("Reservation must end after it starts")

            # don't allow reservations less than a week in the future
            # (which includes reservations in the past)
            if (reservation.start_time
                and reservation.start_time < datetime.now() + timedelta(weeks=1)):
                errors.append("Reservations must be at least one week in the future")

            # look for conflicts
            if date and start_time and end_time:
                conflicts = reservation.check_for_conflicts(resources)
                for conflict in conflicts:
                    message = "Reservation conflicts with '%s' event for %s." % (
                        conflict.event, conflict.camp.name)
                
                    # figure out which resources conflict
                    used_resources = [resource for resource in conflict.resources.all()
                                      if resource.id in resource_ids]
                    message += " They are using %s from %s to %s." % (
                        ", ".join([resource.name for resource in used_resources]),
                        conflict.start_time.strftime(settings.TIME_FORMAT),
                        conflict.end_time.strftime("%I:%M%P"))
                
                    errors.append(message)

            # save the reservation if there were no errors
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
        form_values['date_value'] = reservation.start_time.strftime(settings.DATE_FORMAT)
        form_values['start_time_value'] = reservation.start_time.strftime(
            settings.TIME_FORMAT)
        form_values['end_time_value'] = reservation.end_time.strftime(settings.TIME_FORMAT)
        form_values['reservation_id'] = reservation_id

    form_values['error_messages'] = errors
    if reservation_id:
        form_values['action'] = '/reservation/edit/%s/' % reservation_id
    else:
        form_values['action'] = '/reservation/create/'

    return render(request, 'reservations/addedit.html', form_values)

