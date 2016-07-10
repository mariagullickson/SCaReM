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
