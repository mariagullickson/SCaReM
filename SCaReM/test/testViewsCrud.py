from django.test import TestCase
from django.http import HttpRequest, QueryDict
from SCaReM import views_crud
from SCaReM.models import Reservation, Resource, Camp


class TestViewsCrud(TestCase):
    def setUp(self):
        # gotta have a camp
        self.camp = Camp.objects.create(name="camp pmac")

        # gotta have a resource
        self.resource = Resource.objects.create(name="third floor attic")

    def testAssembleReservationHappyPath(self):
        request = HttpRequest()
        request.POST = QueryDict('', mutable=True)
        request.POST.update({
            'reservation_id': 11,
            'event': 'Dance',
            'owner': 'Wilmur',
            'notes': 'This will be fun',
            'camp': self.camp.id,
            'resources': self.resource.id,
            'date': '08/04/2030',
            'start_time': '10:00 AM',
            'end_time': '11:00 AM',
        })
        form_values = {}
        (reservation, resources, error) = views_crud._assemble_reservation(
            request, form_values)

        self.assertFalse(error)
        self.assertEqual(1, len(resources))
        self.assertEqual(self.resource.id, resources[0].id)
        self.assertEqual(11, reservation.id)
        self.assertEqual('Dance', reservation.event)
        self.assertEqual('Wilmur', reservation.owner)
        self.assertEqual('This will be fun', reservation.notes)
        self.assertEqual(self.camp.id, reservation.camp.id)
        self.assertEqual(2030, reservation.start_time.year)
        self.assertEqual(8, reservation.start_time.month)
        self.assertEqual(4, reservation.start_time.day)
        self.assertEqual(10, reservation.start_time.hour)
        self.assertEqual(0, reservation.start_time.minute)
        self.assertEqual(2030, reservation.end_time.year)
        self.assertEqual(8, reservation.end_time.month)
        self.assertEqual(4, reservation.end_time.day)
        self.assertEqual(11, reservation.end_time.hour)
        self.assertEqual(0, reservation.end_time.minute)
        self.assertEqual([self.resource.id], form_values['resource_values'])
        self.assertEqual(11, form_values['reservation_id'])
        self.assertEqual('Dance', form_values['event_value'])
        self.assertEqual('Wilmur', form_values['owner_value'])
        self.assertEqual('This will be fun', form_values['notes_value'])
        self.assertEqual(self.camp.id, form_values['camp_value'])
        self.assertEqual('08/04/2030', form_values['date_value'])
        self.assertEqual('10:00 AM', form_values['start_time_value'])
        self.assertEqual('11:00 AM', form_values['end_time_value'])
