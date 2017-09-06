from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import RideInformation


class PublicUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'groups',)
        read_only_fields = ('username',)


class PrivateUserSerializer(PublicUserSerializer):
    class Meta(PublicUserSerializer.Meta):
        fields = list(PublicUserSerializer.Meta.fields) + ['auth_token']


class RideSerializer(serializers.ModelSerializer):
    driver = PublicUserSerializer(allow_null=True, required=False)
    passenger = PublicUserSerializer(allow_null=True, required=False)

    def create(self, validated_data):
        data = validated_data.pop('passenger', None)
        ride = super().create(validated_data)
        if data:
            ride.passenger = get_user_model().objects.get(**data)
        ride.save()
        return ride

    def update(self, instance, validated_data):
        data = validated_data.pop('driver', None)
        if data:
            instance.driver = get_user_model().objects.get(**data)
        instance = super().update(instance, validated_data)
        return instance

    class Meta:
        model = RideInformation
        fields = '__all__'
        read_only_fields = ('id', 'nk', 'created', 'updated')