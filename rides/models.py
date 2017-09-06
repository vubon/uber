import datetime
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import reverse

# Create your models here.


class RideInformation(models.Model):
    REQUESTED = 'REQUESTED'
    STARTED = 'STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    TRIP_STATUSES = (
        (REQUESTED, REQUESTED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
    )
    nk = models.CharField(max_length=32, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=100)
    current_location = models.CharField(max_length=200)
    destination_location = models.CharField(max_length=200)
    distance = models.IntegerField()
    status = models.CharField(max_length=20, choices=TRIP_STATUSES, default=REQUESTED)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='rides_as_driver')
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='rides_as_passenger')

    def save(self, **kwargs):
        if not self.nk:
            now = datetime.datetime.now()
            secure_hash = hashlib.md5()
            data = '{now}:{current_location}:{destination_location}:{phone_number}:{distance}'.format(now=now, current_location=self.current_location,destination_location=self.destination_location, phone_number=self.phone_number, distance=self.distance)
            secure_hash.update(data.encode('utf-8'))
            self.nk = secure_hash.hexdigest()
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('ride:ride-details', kwargs={'ride_nk': self.nk})

    def __str__(self):
        return self.current_location + ' To ' + self.destination_location
