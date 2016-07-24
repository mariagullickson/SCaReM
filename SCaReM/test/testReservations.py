from django.test import TestCase
from datetime import datetime
from SCaReM.models import Reservation, Resource, Camp

class TestReservations(TestCase):
    def setUp(self):
        # gotta have a camp
        self.camp = Camp.objects.create(name="camp saint tobias")
        
        # create some resources
        self.resources = []
        self.resources.append(Resource.objects.create(name="bathtub graveyard"))
        self.resources.append(Resource.objects.create(name="cat hall"))
        self.resources.append(Resource.objects.create(name="barrington bunny"))
        
        # create a reservation
        reservation = Reservation.objects.create(start_time = datetime(2000, 1, 15, 12, 30),
                                                 end_time = datetime(2000, 1, 15, 13, 30),
                                                 camp = self.camp)
        reservation.resources = [self.resources[0], self.resources[1]]
        reservation.save()

    def test_no_conflict_immediately_after(self):
        # set up a reservation that starts as another ends.
        # should not see any conflicts
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 13, 30)
        reservation.end_time = datetime(2000, 1, 15, 15, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertFalse(conflicts)

    def test_no_conflict_before(self):
        # set up a reservation that ends as another begins.
        # should not see any conflicts
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 11, 00)
        reservation.end_time = datetime(2000, 1, 15, 12, 30)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertFalse(conflicts)

    def test_no_conflict_after(self):
        # set up a reservation that starts after another.
        # should not see any conflicts
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 14, 00)
        reservation.end_time = datetime(2000, 1, 15, 15, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertFalse(conflicts)

    def test_no_conflict_before(self):
        # set up a reservation that ends before another.
        # should not see any conflicts
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 11, 00)
        reservation.end_time = datetime(2000, 1, 15, 12, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertFalse(conflicts)

    def test_conflicts_arent_duplicated(self):
        # set up a reservation that conflicts with multiple resources for a single other event
        # should only get one conflict
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 12, 00)
        reservation.end_time = datetime(2000, 1, 15, 14, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[1]])
        self.assertEqual(1, len(conflicts))

    def test_no_conflicts_for_different_resource(self):
        # set up a reservation that would conflict on time, but is using different resources.
        # should not see any conflicts
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 12, 00)
        reservation.end_time = datetime(2000, 1, 15, 14, 00)
        conflicts = reservation.check_for_conflicts([self.resources[2]])
        self.assertFalse(conflicts)

    def test_conflicts_fully_contained(self):
        # set up a reservation that starts after another and ends before it.
        # should see a conflict if it's using one of the same resources
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 12, 00)
        reservation.end_time = datetime(2000, 1, 15, 14, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertEqual(1, len(conflicts))

    def test_conflicts_fully_containing(self):
        # set up a reservation that starts before another and ends after it.
        # should see a conflict if it's using one of the same resources
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 12, 00)
        reservation.end_time = datetime(2000, 1, 15, 14, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertEqual(1, len(conflicts))

    def test_conflicts_overlapping_end(self):
        # set up a reservation whose end time overlaps with an existing reservation.
        # should see a conflict if it's using one of the same resources
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 12, 00)
        reservation.end_time = datetime(2000, 1, 15, 13, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertEqual(1, len(conflicts))
        
    def test_conflicts_overlapping_start(self):
        # set up a reservation whose start time overlaps with an existing reservation.
        # should see a conflict if it's using one of the same resources
        reservation = Reservation()
        reservation.start_time = datetime(2000, 1, 15, 13, 00)
        reservation.end_time = datetime(2000, 1, 15, 14, 00)
        conflicts = reservation.check_for_conflicts([self.resources[0], self.resources[2]])
        self.assertEqual(1, len(conflicts))

        
