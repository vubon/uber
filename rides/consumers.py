from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer
from .models import RideInformation
from .serializers import RideSerializer


class RideConsumer(JsonWebsocketConsumer):
    http_user_and_session = True

    def user_rides(self):
        raise NotImplementedError()

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({'accept': True})
        if self.message.user.is_authenticated:
            ride_nks = [trip.nk for trip in self.user_rides()]
            self.message.channel_session['ride_nks'] = ride_nks
            for ride_nk in ride_nks:
                Group(ride_nk).add(self.message.reply_channel)

    def disconnect(self, message, **kwargs):
        for ride_nk in message.channel_session.get('ride_nks', []):
            Group(ride_nk).discard(message.reply_channel)


class DriverConsumer(RideConsumer):
    groups = ['drivers']

    def user_rides(self):
        return self.message.user.rides_as_driver.exclude(status=RideInformation.COMPLETED)

    def connect(self, message, **kwargs):
        super().connect(message, **kwargs)
        Group('drivers').add(self.message.reply_channel)

    def receive(self, content, **kwargs):
        """Drivers should send ride status updates."""

        # Update an existing ride from the incoming data.
        ride = RideInformation.objects.get(nk=content.get('nk'))
        serializer = RideSerializer(data=content)
        serializer.is_valid(raise_exception=True)
        ride = serializer.update(ride, serializer.validated_data)

        # Subscribe driver to messages regarding the existing ride.
        # Driver will receive updates about existing ride.
        self.message.channel_session['ride_nks'].append(ride.nk)
        Group(ride.nk).add(self.message.reply_channel)
        rides_data = RideSerializer(ride).data
        self.group_send(name=ride.nk, content=rides_data)


class PassengerConsumer(RideConsumer):
    def user_rides(self):
        return self.message.user.rides_as_passenger.exclude(status=RideInformation.COMPLETED)

    def receive(self, content, **kwargs):
        """passenger should only ever send a request to create a new ride."""

        # Create a new ride from the incoming data.
        serializer = RideSerializer(data=content)
        serializer.is_valid(raise_exception=True)
        ride = serializer.create(serializer.validated_data)

        # Subscribe Passenger to messages regarding the newly created ride.
        # Passenger will receive updates from driver.
        self.message.channel_session['ride_nks'].append(ride.nk)
        Group(ride.nk).add(self.message.reply_channel)
        rides_data = RideSerializer(ride).data
        self.group_send(name=ride.nk, content=rides_data)

        # Alert all drivers that a new trip has been requested.
        self.group_send(name='drivers', content=rides_data)

