from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Passenger(models.Model):
    user = models.OneToOneField(User, related_name='rides_as_passenger')

    def __str__(self):
        return self.user.get_full_name()


class Driver(models.Model):
    user = models.OneToOneField(User, related_name='rides_as_driver')

    def __str__(self):
        return self.user.get_full_name()


class RideInformation(models.Model):
    passenger = models.ForeignKey(Passenger, null=True, blank=True, related_name='rides_as_passenger')
    driver = models.ForeignKey(Driver, null=True, blank=True, related_name='rides_as_driver')
    phone_number = models.CharField(max_length=100)
    current_location = models.CharField(max_length=200)
    destination_location = models.CharField(max_length=200)
    distance = models.IntegerField()

    def __str__(self):
        return self.current_location + ' To ' + self.destination_location

    class Meta:
        ordering = ('driver',)