from django.db import models

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

    def resource_names(self):
        return ", ".join([r.name for r in self.resources.all()])

    def check_for_conflicts(self, resources):
        # look for conflicts with each resource.  the way we are
        # querying could produce duplicates, so shove them into a dict
        # by id to eliminate those.
        conflicts = {}
        for resource in resources:
            resource_conflicts = Reservation.objects.filter(
                resources__id__exact=resource.id).filter(
                    start_time__lt = self.end_time).filter(
                        end_time__gt = self.start_time)
            for conflict in resource_conflicts:
                conflicts[conflict.id] = conflict

        # if we are editing an existing reservation, we probably found a
        # "conflict" with ourself.  obviously that's not a real conflict,
        # so remove it if it's there
        if self.id in conflicts:
            del conflicts[self.id]
                
        return conflicts.values()
