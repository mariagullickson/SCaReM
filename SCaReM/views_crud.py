from datetime import datetime, timedelta
import json
from copy import deepcopy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
import models
import settings

EASTER_EGG_KEY = 'easter'
LAST_CAMP_KEY = 'last_camp_id'
LAST_OWNER_KEY = 'last_owner'

EASTER_EGGS = {
    "Dance!": "dance",
    "Dutch Auction!": "dutchauction",
    "Hayride!": "hayride",
    "Kangaroo Court!": "kangaroocourt",
    "Movie Night!": "movienight",
    "Pool Party!": "poolparty",
    "Scavenger Hunt!": "scavengerhunt",
    "Olympics!": "olympics",
    "King Ball!": "kingball",
    }


def delete_reservation(request, reservation_id=None):
    reservation = get_object_or_404(models.Reservation, pk=reservation_id)

    # if this is a recurring reservation, make sure we are deleting the
    # primary event
    if (reservation.recurrence_id
        and reservation.recurrence_id != reservation.id):
        return HttpResponseRedirect('/reservation/delete/%s'
                                    % reservation.recurrence_id)

    if 'confirmed' in request.GET and request.GET['confirmed'] == 'true':
        # they've confirmed.  actually delete the reservation and go
        # back to the index.  if it's a recurrence, delete them all
        if reservation.recurrence_id:
            for recurrence in reservation.recurrences():
                recurrence.delete()
        reservation.delete()
        messages.success(request,
                         "%s %s has been deleted"
                         % (reservation.camp.name, reservation.event))
        return redirect('/')

    # show the confirmation page before doing anything
    messages.warning(request,
                     'Are you sure you want to delete this reservation?')
    if reservation.recurrence_id:
        messages.warning(request, 'This is a recurring reservation. '
                         'All events will be deleted.')
    data = {
        'reservation': reservation
    }
    return render(request, 'reservations/delete.html', data)


def __assemble_reservation(request, form_values):
    reservation = models.Reservation()
    error = False

    # put together the reservation object
    if 'reservation_id' in request.POST and request.POST['reservation_id']:
        reservation.id = int(request.POST['reservation_id'])
        form_values['reservation_id'] = reservation.id

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

    reservation.notes = request.POST['notes']
    form_values['notes_value'] = reservation.notes

    camp_id = request.POST['camp']
    if not camp_id:
        messages.error(request, "You must specify a Camp.")
        error = True
    else:
        reservation.camp = get_object_or_404(models.Camp, pk=camp_id)
        form_values['camp_value'] = reservation.camp.id

    resource_ids = [int(x) for x in request.POST.getlist('resources')]
    resources = [get_object_or_404(models.Resource, pk=resource_id)
                 for resource_id in resource_ids]
    if not resources:
        messages.error(request, "You must specify at least one Resource.")
        error = True
    form_values['resource_values'] = [resource.id for resource in resources]

    date = request.POST['date']
    if date:
        try:
            datetime.strptime(date, settings.DATE_FORMAT)
            form_values['date_value'] = date
        except:
            messages.error(request,
                           "Invalid Date. Should be formatted as MM/DD/YYYY.")
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
                           "Should be formatted as HH:MM {am/pm}.")
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
                           "Should be formatted as HH:MM {am/pm}.")
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
        messages.error(request, "Reservation must end after it starts.")
        error = True

    # don't allow reservations less than a week in the future
    # (which includes reservations in the past)
    if reservation.start_time and reservation.is_frozen():
        messages.error(request, "Reservations must be at least one "
                       "week in the future.")
        error = True

    # look for conflicts
    if date and start_time and end_time:
        if __check_for_conflicts(reservation, resources, request):
            error = True

    return (reservation, resources, error)


def __check_for_conflicts(reservation, resources, request,
                          ignore_recurrence=None):
    conflicts = reservation.check_for_conflicts(resources, ignore_recurrence)
    resource_ids = [resource.id for resource in resources]
    if not conflicts:
        return False

    for conflict in conflicts:
        message = ("Reservation conflicts with '%s' event for %s."
                   % (conflict.event, conflict.camp.name))

        # figure out which resources conflict
        used_resources = [resource for resource in conflict.resources.all()
                          if resource.id in resource_ids
                          and not resource.allow_conflicts]
        message += " They are using %s from %s to %s on %s." % (
            ", ".join([resource.name for resource in used_resources]),
            conflict.start_time.strftime(settings.TIME_FORMAT),
            conflict.end_time.strftime(settings.TIME_FORMAT),
            conflict.start_time.strftime(settings.DATE_FORMAT))

        messages.error(request, message)

    return True


def __assemble_recurrences(request, form_values, reservation, resources):
    error = False
    recurrences_to_save = []

    # if there are existing recurrences, remove them.  we'll recreate them
    # as needed.  this is just easier.
    recurrences_to_remove = reservation.recurrences()
    reservation.recurrence_id = None

    # if this isn't a recurrence, we have nothing to add.  if it used
    # to be a recurrence, clear out the recurrence_id
    if 'repeat_until' not in request.POST or not request.POST['repeat_until']:
        if reservation.recurrence_id:
            reservation.recurrence_id = None
        return (recurrences_to_save, recurrences_to_remove, error)

    # parse out the end date for the recurrence
    end_time = None
    end_date = None
    try:
        end_date = datetime.strptime(request.POST['repeat_until'],
                                     settings.DATE_FORMAT)
        form_values['repeat_until_value'] = request.POST['repeat_until']
        end_time = end_date + timedelta(hours=23, minutes=59)
    except:
        messages.error(request, "Invalid Repeat Daily Until. "
                       "Should be formatted as MM/DD/YYYY.")
        error = True
        return (recurrences_to_save, recurrences_to_remove, error)

    # end date must be at least 1 day and no more than 90 days after start
    num_days = (end_time - reservation.start_time).days
    if num_days < 1:
        messages.error(request, "Repeat Daily Until must be later than Date.")
        error = True
        return (recurrences_to_save, recurrences_to_remove, error)
    if num_days > 90:
        messages.error(request, "Reservations cannot repeat more than 90 days.")
        error = True
        return (recurrences_to_save, recurrences_to_remove, error)

    # assemble the recurrences
    next_start = reservation.start_time + timedelta(days=1)
    next_end = reservation.end_time + timedelta(days=1)
    while next_start < end_time:
        # assemble the recurrence
        recurrence = deepcopy(reservation)
        recurrence.id = None
        recurrence.start_time = next_start
        recurrence.end_time = next_end

        # add it to the list
        recurrences_to_save.append(recurrence)

        # check for conflicts on this one
        ignore_recurrence = None
        if 'reservation_id' in form_values:
            ignore_recurrence = form_values['reservation_id']
        if __check_for_conflicts(recurrence, resources, request,
                                 ignore_recurrence):
            error = True

        # incrememt for the next one
        next_start = next_start + timedelta(days=1)
        next_end = next_end + timedelta(days=1)

    return (recurrences_to_save, recurrences_to_remove, error)


def __save_reservation(request, form_values):
    try:
        (reservation, resources, reservation_error) = __assemble_reservation(
            request, form_values)

        (save_recurrences, remove_recurrences, recurrence_error) = \
            __assemble_recurrences(
                request, form_values, reservation, resources)

        # check for errors before we save
        if reservation_error or recurrence_error:
            return render(request, 'reservations/addedit.html', form_values)

        
        # save the reservation
        is_new = not reservation.id

        # if it's a new reservation, check for an easter egg
        if is_new and reservation.event in EASTER_EGGS:
            request.session[EASTER_EGG_KEY] = EASTER_EGGS[reservation.event]
        elif EASTER_EGG_KEY in request.session:
            del request.session[EASTER_EGG_KEY]

        # save the basic reservation
        reservation.save()

        # attach the resources and save again
        reservation.resources = resources
        reservation.save(False)

        # if there are recurrences to remove, do that
        if remove_recurrences:
            for recurrence in remove_recurrences:
                recurrence.delete()

        # if there are recurrences to add, do a bunch more saving
        if save_recurrences:
            reservation.recurrence_id = reservation.id
            reservation.save()
                
            for recurrence in save_recurrences:
                recurrence.recurrence_id = reservation.id
                recurrence.save()

                recurrence.resources = resources
                recurrence.save()
            
        messages.success(request, "%s %s has been %s"
                         % (reservation.camp.name, reservation.event,
                            "created" if is_new else "updated"))

        # remember this users camp and owner name
        request.session[LAST_CAMP_KEY] = reservation.camp.id
        request.session[LAST_OWNER_KEY] = reservation.owner

        if 'another' in request.POST:
            return HttpResponseRedirect('/reservation/create')

        return HttpResponseRedirect('/')
    except Exception as e:
        messages.error(request, e.message or e.args[1])

    return render(request, 'reservations/addedit.html', form_values)
    

def __populate_existing_reservation(reservation_id, request, form_values):
    # editing an existing reservation.  load it from the database
    # and fill in form fields
    reservation = get_object_or_404(models.Reservation, pk=reservation_id)

    # if this is a recurring reservation, make sure we are editing the
    # primary event
    if (reservation.recurrence_id
        and reservation.recurrence_id != reservation.id):
        return HttpResponseRedirect('/reservation/edit/%s'
                                    % reservation.recurrence_id)

    if reservation.recurrence_id:
        messages.warning(request, 'This is a recurring reservation. '
                         'Any changes will apply to all events.')
        last_recurrence = reservation.recurrences().last()
        form_values['repeat_until_value'] = last_recurrence.start_time.strftime(
            settings.DATE_FORMAT)
    
    form_values['event_value'] = reservation.event
    form_values['owner_value'] = reservation.owner
    form_values['notes_value'] = reservation.notes
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
    return render(request, 'reservations/addedit.html', form_values)


def __populate_blank_reservation(request, form_values):
    # if we are starting a fresh reservation, prefill camp and owner
    # with the last values used in this session
    if LAST_OWNER_KEY in request.session:
        form_values['owner_value'] = request.session[LAST_OWNER_KEY]
    if LAST_CAMP_KEY in request.session:
        form_values['camp_value'] = request.session[LAST_CAMP_KEY]
    return render(request, 'reservations/addedit.html', form_values)


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
        'resources': models.Resource.objects.all().order_by('name'),
        'tags': models.Tag.objects.all(),
        'tag_resources': json.dumps(tag_resources),
    }

    if reservation_id:
        form_values['action'] = '/reservation/edit/%s/' % reservation_id
    else:
        form_values['action'] = '/reservation/create/'

    if request.method == 'POST':
        return __save_reservation(request, form_values)
    elif reservation_id:
        return __populate_existing_reservation(reservation_id, request,
                                               form_values)
    else:
        return __populate_blank_reservation(request, form_values)
