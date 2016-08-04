from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
import models
from datetime import datetime
import json
import settings


EASTER_EGGS = {
    "Dance!": "dance",
    "Dutch Auction!": "dutchauction",
    "Hayride!": "hayride",
    "Kangaroo Court!": "kangaroocourt",
    "Movie Night!": "movienight",
    "Pool Party!": "poolparty",
    "Scavenger Hunt!": "scavengerhunt",
    }


def delete_reservation(request, reservation_id=None):
    reservation = get_object_or_404(models.Reservation, pk=reservation_id)

    if 'confirmed' in request.GET and request.GET['confirmed'] == 'true':
        # they've confirmed.  actually delete the reservation and got
        # back to the index
        reservation.delete()
        messages.success(request,
                         "%s %s has been deleted"
                         % (reservation.camp.name, reservation.event))
        return redirect('/')
    else:
        # show the confirmation page before doing anything
        data = {
            'reservation': reservation
        }
        return render(request, 'reservations/delete.html', data)


def create_or_edit_reservation(request, reservation_id=None):
    resources = models.Resource.objects.all()
    tag_resources = {}
    error = False
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

    if request.method == 'POST':
        try:
            # put together the reservation object
            reservation = models.Reservation()
            if ('reservation_id' in request.POST and
                    request.POST['reservation_id']):
                reservation.id = int(request.POST['reservation_id'])

            reservation.event = request.POST['event']
            if not reservation.event:
                messages.error(request, "You must specify an Event.")
                error = True
            form_values['event_value'] = reservation.event

            reservation.owner = request.POST['owner']
            if not reservation.owner:
                messages.error(request, "You must specify an Owner.")
                error = True
            form_values['owner_value'] = reservation.owner

            camp_id = request.POST['camp']
            if not camp_id:
                messages.error(request, "You must specify a Camp.")
                error = True
            else:
                reservation.camp = get_object_or_404(models.Camp, pk=camp_id)
                form_values['camp_value'] = reservation.camp.id

            resource_ids = [int(x) for x in request.POST.getlist('resources')]
            resources = [
                get_object_or_404(models.Resource, pk=resource_id)
                for resource_id in resource_ids]
            if not resources:
                messages.error(request,
                               "You must specify at least one Resource.")
                error = True
            form_values['resource_values'] = [
                resource.id for resource in resources]

            date = request.POST['date']
            if date:
                try:
                    datetime.strptime(date, settings.DATE_FORMAT)
                    form_values['date_value'] = date
                except:
                    messages.error(request, "Invalid Date. "
                                   "Should be formatted as MM/DD/YYYY.")
                    error = True
                    date = None
            else:
                messages.error(request, "You must specify a Date.")
                error = True

            start_time = request.POST['start_time']
            if start_time:
                try:
                    datetime.strptime(start_time, settings.TIME_FORMAT)
                    form_values['start_time_value'] = start_time
                except:
                    messages.error(request, "Invalid Start Time. "
                                   "Should be formatted as HH : MM {am/pm}.")
                    error = True
                    start_time = None
            else:
                messages.error(request, "You must specify a Start Time.")
                error = True

            end_time = request.POST['end_time']
            if end_time:
                try:
                    datetime.strptime(end_time, settings.TIME_FORMAT)
                    form_values['end_time_value'] = end_time
                except:
                    messages.error(request, "Invalid End Time. "
                                   "Should be formatted as HH : MM {am/pm}.")
                    error = True
                    end_time = None
            else:
                messages.error(request, "You must specify a End Time.")
                error = True

            if date and start_time:
                reservation.start_time = datetime.strptime(
                    "%s %s" % (date, start_time),
                    settings.DATETIME_FORMAT)
            if date and end_time:
                reservation.end_time = datetime.strptime(
                    "%s %s" % (date, end_time),
                    settings.DATETIME_FORMAT)
            if (reservation.start_time and reservation.end_time and
                    reservation.end_time <= reservation.start_time):
                messages.error(request,
                               "Reservation must end after it starts.")
                error = True

            # don't allow reservations less than a week in the future
            # (which includes reservations in the past)
            if reservation.start_time and reservation.is_frozen():
                messages.error(request, "Reservations must be at least one "
                               "week in the future.")
                error = True

            # look for conflicts
            if date and start_time and end_time:
                conflicts = reservation.check_for_conflicts(resources)
                for conflict in conflicts:
                    message = ("Reservation conflicts with '%s' event for %s."
                               % (conflict.event, conflict.camp.name))

                    # figure out which resources conflict
                    used_resources = [resource for resource
                                      in conflict.resources.all()
                                      if resource.id in resource_ids]
                    message += " They are using %s from %s to %s." % (
                        ", ".join([resource.name for resource
                                   in used_resources]),
                        conflict.start_time.strftime(settings.TIME_FORMAT),
                        conflict.end_time.strftime("%I:%M%P"))

                    messages.error(request, message)
                    error = True

            # save the reservation if there were no errors
            if not error:
                # if it's a new reservation, check for an easter egg
                if not reservation.id and reservation.event in EASTER_EGGS:
                    request.session['easter'] = EASTER_EGGS[reservation.event]

                reservation.save()
                reservation.resources = resources
                reservation.save(False)

                # remember this users camp and owner name
                request.session['last_camp_id'] = reservation.camp.id
                request.session['last_owner'] = reservation.owner

                return HttpResponseRedirect('/')
        except Exception as e:
            messages.error(request, e.message or e.args[1])
    elif reservation_id:
        # editing an existing reservation.  load it from the database
        # and fill in form fields
        reservation = get_object_or_404(models.Reservation, pk=reservation_id)
        form_values['event_value'] = reservation.event
        form_values['owner_value'] = reservation.owner
        form_values['camp_value'] = reservation.camp.id
        form_values['resource_values'] = [
            resource.id for resource in reservation.resources.all()]
        form_values['date_value'] = reservation.start_time.strftime(
            settings.DATE_FORMAT)
        form_values['start_time_value'] = reservation.start_time.strftime(
            settings.TIME_FORMAT)
        form_values['end_time_value'] = reservation.end_time.strftime(
            settings.TIME_FORMAT)
        form_values['reservation_id'] = reservation_id
    else:
        # if we are starting a fresh reservation, prefill camp and owner
        # with the last values used in this session
        if 'last_owner' in request.session:
            form_values['owner_value'] = request.session['last_owner']
        if 'last_camp_id' in request.session:
            form_values['camp_value'] = request.session['last_camp_id']

    if reservation_id:
        form_values['action'] = '/reservation/edit/%s/' % reservation_id
    else:
        form_values['action'] = '/reservation/create/'

    return render(request, 'reservations/addedit.html', form_values)
