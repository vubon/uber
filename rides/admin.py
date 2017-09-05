from django.contrib import admin
from .models import Passenger, RideInformation, Driver

# Register your models here.
admin.site.register(Passenger)
admin.site.register(Driver)
admin.site.register(RideInformation)
