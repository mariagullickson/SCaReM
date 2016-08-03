from django.db import models
from datetime import datetime, timedelta


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class Camp(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    event = models.CharField(max_length=100)
    owner = models.CharField(max_length=50)
    camp = models.ForeignKey(Camp)
    resources = models.ManyToManyField(Resource)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "%s %s on %s" % (
            self.camp.name, self.event, self.start_time.date())

    def delete(self):
        # store an audit log entry
        audit = AuditLog()
        audit.reservation_id = self.id
        audit.reservation_representation = str(self)
        audit.action = AuditLog.DELETE
        audit.timestamp = datetime.now()
        audit.save()

        result = super(Reservation, self).delete()
        return result

    def save(self, audit=True, **kwargs):
        is_add = not self.id

        # save the reservation
        result = super(Reservation, self).save()

        # store an audit log entry
        if audit:
            audit = AuditLog()
            audit.reservation_id = self.id
            audit.reservation_representation = str(self)
            audit.action = AuditLog.ADD if is_add else AuditLog.MODIFY
            audit.timestamp = datetime.now()
            audit.save(**kwargs)

        return result

    def resource_names(self):
        return ", ".join([r.name for r in self.resources.all()])

    def is_frozen(self):
        return self.start_time < datetime.now() + timedelta(weeks=1)

    def check_for_conflicts(self, resources):
        # look for conflicts with each resource.  the way we are
        # querying could produce duplicates, so shove them into a dict
        # by id to eliminate those.
        conflicts = {}
        for resource in resources:
            resource_conflicts = Reservation.objects.filter(
                resources__id__exact=resource.id).filter(
                    start_time__lt=self.end_time).filter(
                        end_time__gt=self.start_time)
            for conflict in resource_conflicts:
                conflicts[conflict.id] = conflict

        # if we are editing an existing reservation, we probably found a
        # "conflict" with ourself.  obviously that's not a real conflict,
        # so remove it if it's there
        if self.id in conflicts:
            del conflicts[self.id]

        return conflicts.values()


class AuditLog(models.Model):
    ADD = 'add'
    DELETE = 'delete'
    MODIFY = 'modify'
    ACTION_CHOICES = (
        (ADD, 'Add'),
        (DELETE, 'Delete'),
        (MODIFY, 'Modify'),
        )

    # This is intentionally not a foreign key, because we want auditlog
    # entries to persist after a reservation is deleted
    reservation_id = models.IntegerField()
    reservation_representation = models.CharField(max_length=500)
    timestamp = models.DateTimeField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
