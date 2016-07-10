from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import models
from datetime import datetime

def index(request):
    return HttpResponse('Hello World!')

def create_reservation(request):
    error_message = None

    if request.method == 'POST':
        try:
            # put together the reservation object
            reservation = models.Reservation()

            reservation.event = request.POST['event']
            if not reservation.event:
                raise Exception("You must specify an Event")

            reservation.owner = request.POST['owner']
            if not reservation.owner:
                raise Exception("You must specify an Owner")

            camp_id = request.POST['camp']
            if not camp_id:
                raise Exception("You must specify a Camp")
            reservation.camp = get_object_or_404(models.Camp, pk=camp_id)

            resources = [
                get_object_or_404(models.Resource, pk=resource_id)
                for resource_id in request.POST.getlist('resources')]
            if not resources:
                raise Exception("You must specify at least one Resource")

            import pdb
            pdb.set_trace()
            date = request.POST['date']
            start_time = request.POST['start_time']
            end_time = request.POST['end_time']
            if not date:
                raise Exception("You must specify a Date")
            if not start_time:
                raise Exception("You must specify a Start Time")
            if not end_time:
                raise Exception("You must specify a End Time")
            reservation.start_time = datetime.strptime(
                "%s %s" % (date, start_time),
                "%m/%d/%Y %I:%M%p")
            reservation.end_time = datetime.strptime(
                "%s %s" % (date, end_time),
                "%m/%d/%Y %I:%M%p")
            if reservation.end_time <= reservation.start_time:
                raise Exception("Reservation must end after it starts")
                        
            # save the reservation
            reservation.save()
            reservation.resources = resources
            reservation.save()

            return HttpResponseRedirect('/')
        except Exception as e:
            error_message = e.message or e.args[1]

    return render(request, 'reservations/create.html', {
        'camps': models.Camp.objects.all(),
        'resources': models.Resource.objects.all(),
        'error_message': error_message,
        'data': request.POST,
    })
            
