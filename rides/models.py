from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


# class Passenger(models.Model):
#     user = models.ForeignKey(User, related_name='passenger')
#
#     def __str__(self):
#         return self.user
#
#
# class Driver(models.Model):
#     user = models.ForeignKey(User, related_name='driver')
#
#     def __str__(self):
#         return self.user

class Destination(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class RideInformation(models.Model):
    passenger = models.ManyToManyField(User, related_name='rides_as_passenger')
    driver = models.ForeignKey(User, related_name='rides_as_driver')
    phone_number = models.CharField(max_length=100)
    current_location = models.CharField(max_length=200)
    destination_location = models.ForeignKey(Destination, related_name='rides_as_final_destination')
    distance = models.IntegerField()

    def __str__(self):
        return self.current_location + ' To ' + str(self.destination_location)
