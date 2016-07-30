from django.test import TestCase
from datetime import datetime, date
from SCaReM.models import Reservation, Resource, Camp
from SCaReM import views

class TestReservations(TestCase):
    def setUp(self):
        # gotta have a camp
        self.camp = Camp.objects.create(name="camp pmac")
        
        # gotta have a resource
        self.resource = Resource.objects.create(name="third floor attic")

    def test_group_empty_list_by_day(self):
        # if we pass in an empty list, it should return an empty list
        # and not throw any errors
        groups = views.group_reservations_by_day([])
        self.assertEqual([], groups)

    def test_group_by_day(self):
        # test passing in a list of reservations.  it should return
        # all of them grouped by day
        reservations = [
            self.create_reservation(datetime(2020, 10, 1, 10, 00),
                                    datetime(2020, 10, 1, 11, 00),
                                    "Event 1A"),
            self.create_reservation(datetime(2020, 10, 1, 12, 00),
                                    datetime(2020, 10, 1, 12, 30),
                                    "Event 1B"),
            self.create_reservation(datetime(2020, 10, 3, 18, 00),
                                    datetime(2020, 10, 3, 19, 00),
                                    "Event 2"),
            self.create_reservation(datetime(2020, 10, 4, 12, 00),
                                    datetime(2020, 10, 4, 13, 00),
                                    "Event 3A"),
            self.create_reservation(datetime(2020, 10, 4, 18, 00),
                                    datetime(2020, 10, 4, 20, 00),
                                    "Event 3B"),
            ]
        groups = views.group_reservations_by_day(reservations)
        self.assertEqual(3, len(groups))
        self.assertEqual(date(2020, 10, 1), groups[0][0])
        self.assertEqual(2, len(groups[0][1]))
        self.assertEqual("Event 1A", groups[0][1][0].event)
        self.assertEqual("Event 1B", groups[0][1][1].event)
        self.assertEqual(date(2020, 10, 3), groups[1][0])
        self.assertEqual(1, len(groups[1][1]))
        self.assertEqual("Event 2", groups[1][1][0].event)
        self.assertEqual(date(2020, 10, 4), groups[2][0])
        self.assertEqual(2, len(groups[2][1]))
        self.assertEqual("Event 3A", groups[2][1][0].event)
        self.assertEqual("Event 3B", groups[2][1][1].event)

    def create_reservation(self, start_time, end_time, event):
        reservation = Reservation.objects.create(start_time = start_time,
                                                 end_time = end_time,
                                                 event = event,
                                                 camp = self.camp)
        reservation.resources = [self.resource]
        return reservation

