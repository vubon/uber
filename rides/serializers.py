from rest_framework import serializers
from .models import RideInformation, Driver, Passenger
from django.contrib.auth import get_user_model
from django.utils.timezone import now


class PublicUserSerializer(serializers.ModelSerializer):
    # groups = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username',)
        read_only_fields = ('username',)


class RideSerializer(serializers.ModelSerializer):
    driver = PublicUserSerializer(allow_null=True, required=False)
    passenger = PublicUserSerializer(allow_null=True, required=False)
    # driver = serializers.IntegerField(source='driver.id', read_only=True)

    def create(self, validated_data):
        data = validated_data.pop('passenger', None)
        trip = super().create(validated_data)
        if data:
            trip.passenger = Passenger.objects.get(**data)
            # trip.rider = get_user_model().objects.get(**data)
        trip.save()
        return trip

    def update(self, instance, validated_data):
        data = validated_data.pop('driver', None)
        if data:
            instance.driver = Driver.objects.get(**data)
            # instance.driver = get_user_model().objects.get(**data)
        instance = super().update(instance, validated_data)
        return instance

    class Meta:
        depth = 1
        model = RideInformation
        fields =  '__all__'  # ('id', 'driver', 'current_location', 'destination_location', 'phone_number', 'distance')
        read_only_fields = ('id', 'driver', 'passenger')


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 1
        model = Driver
        fields = '__all__'


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 1
        model = Passenger
        fields = '__all__'