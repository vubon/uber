from rest_framework import serializers
from .models import RideInformation


class RideSerializer(serializers.ModelSerializer):
    driver = serializers.ReadOnlyField(source='driver.username')

    class Meta:
        model = RideInformation
        fields = ('id', 'driver', 'destination', 'passengers')
        read_only_fields = ('id', 'driver', 'passengers')