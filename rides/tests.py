from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as AuthGroup
from channels import Group
from channels.test import ChannelTestCase, HttpClient
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APIClient, APITestCase
from .models import RideInformation
from .serializers import PublicUserSerializer, PrivateUserSerializer, RideSerializer

PASSWORD = 'password!'


def create_user(username='user@vubon.com', password=PASSWORD, group='passenger'):
    auth_group, _ = AuthGroup.objects.get_or_create(name=group)
    user = get_user_model().objects.create_user(username=username, password=password)
    user.groups.add(auth_group)
    user.save()
    return user


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_can_sign_up(self):
        response = self.client.post(reverse('sign_up'), data={
            'username': 'user@vubon.com',
            'password1': PASSWORD,
            'password2': PASSWORD
        })
        user = get_user_model().objects.last()
        self.assertEqual(HTTP_201_CREATED, response.status_code)
        self.assertEqual(PublicUserSerializer(user).data, response.data)

    def test_user_can_log_in(self):
        user = create_user()
        response = self.client.post(reverse('log_in'), data={
            'username': user.username,
            'password': PASSWORD,
        })
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(PrivateUserSerializer(user).data, response.data)
        self.assertIsNotNone(Token.objects.get(user=user))

    def test_user_can_log_out(self):
        user = create_user()
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=token))
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.post(reverse('log_out'))
        self.assertEqual(HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(Token.objects.filter(user=user).exists())


class HttpRideTest(APITestCase):
    def setUp(self):
        self.user = create_user()
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=token))

    def test_user_can_list_personal_rides(self):
        rides = [
            RideInformation.objects.create(current_location='A', destination_location='B', phone_number='01737378829', distance=11, passenger=self.user),
            RideInformation.objects.create(current_location='B', destination_location='C', phone_number='01737378829', distance=11, passenger=self.user),
            RideInformation.objects.create(current_location='C', destination_location='D', phone_number='01737378829', distance=11)
        ]
        response = self.client.get(reverse('ride:ride_list'))
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(RideSerializer(rides[0:2], many=True).data, response.data)

    def test_user_can_retrieve_personal_ride_by_nk(self):
        ride = RideInformation.objects.create(current_location='A', destination_location='B',phone_number='01737378829', distance=11, passenger=self.user)
        response = self.client.get(ride.get_absolute_url())
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(RideSerializer(ride).data, response.data)


class WebSocketRideTest(ChannelTestCase):
    def setUp(self):
        self.driver = create_user(username='driver@example.com', group='driver')
        self.passenger = create_user(username='passenger@example.com', group='passenger')

    def connect_as_driver(self, driver):
        client = HttpClient()
        client.login(username=driver.username, password=PASSWORD)
        client.send_and_consume('websocket.connect', path='/driver/')
        return client

    def connect_as_passenger(self, passenger):
        client = HttpClient()
        client.login(username=passenger.username, password=PASSWORD)
        client.send_and_consume('websocket.connect', path='/passenger/')
        return client

    def create_ride(self, passenger, current_location='A', destination_location='B', phone_number='01737388290', distance=11):
        client = self.connect_as_passenger(passenger)
        client.send_and_consume('websocket.receive', path='/passenger/', content={
            'text': {
                'current_location': current_location,
                'destination_location': destination_location,
                'phone_number': phone_number,
                'distance': distance,
                'passenger': PublicUserSerializer(passenger).data
            }
        })
        return client

    def update_ride(self, driver, ride, status):
        client = self.connect_as_driver(driver)
        client.send_and_consume('websocket.receive', path='/driver/', content={
            'text': {
                'nk': ride.nk,
                'current_location': ride.current_location,
                'destination_location': ride.destination_location,
                'phone_number': ride.phone_number,
                'distance': ride.distance,
                'status': status,
                'driver': PublicUserSerializer(driver).data
            }
        })
        return client

    def test_driver_can_connect_via_websockets(self):
        client = HttpClient()
        client.login(username=self.driver.username, password='password!')
        client.send_and_consume('websocket.connect', path='/driver/')
        message = client.receive()
        self.assertIsNone(message)

    def test_passenger_can_connect_via_websockets(self):
        client = HttpClient()
        client.login(username=self.passenger.username, password='password!')
        client.send_and_consume('websocket.connect', path='/passenger/')
        message = client.receive()
        self.assertIsNone(message)

    def test_passenger_can_create_rides(self):
        client = self.create_ride(self.passenger)
        ride = RideInformation.objects.last()
        self.assertEqual(RideSerializer(ride).data, client.receive())

    def test_passenger_is_subscribed_to_ride_channel(self):
        client = self.create_ride(self.passenger)
        client.receive()
        ride = RideInformation.objects.last()
        message = {'message': 'test'}
        Group(ride.nk).send(message)
        self.assertEqual(message, client.receive())

    def test_passenger_is_not_subscribed_to_other_ride_channel(self):
        ride = RideInformation.objects.create(current_location='B', destination_location='C', phone_number='01737388290', distance=11)
        client = self.create_ride(self.passenger)
        client.receive()
        message = {'message': 'test'}
        Group(ride.nk).send(message)
        self.assertIsNone(client.receive())

    def test_driver_is_alerted_on_ride_creation(self):
        client = self.connect_as_driver(self.driver)
        self.create_ride(self.passenger)
        ride = RideInformation.objects.last()
        self.assertEqual(RideSerializer(ride).data, client.receive())

    def test_driver_can_update_rides(self):
        ride = RideInformation.objects.create(current_location='A', destination_location='B', phone_number='01737388290', distance=11)
        client = self.update_ride(self.driver, ride=ride, status=RideInformation.STARTED)
        ride = RideInformation.objects.get(nk=ride.nk)
        self.assertEqual(RideSerializer(ride).data, client.receive())

    def test_driver_is_subscribed_to_ride_channel_on_update(self):
        ride = RideInformation.objects.create(current_location='A', destination_location='B', phone_number='01737388290', distance=11)
        client = self.update_ride(self.driver, ride=ride, status=RideInformation.STARTED)
        client.receive()
        ride = RideInformation.objects.last()
        message = {'detail': 'This is a test message.'}
        Group(ride.nk).send(message)
        self.assertEqual(message, client.receive())

    def test_passenger_is_alerted_on_ride_update(self):
        client = self.create_ride(self.passenger)
        client.receive()
        ride = RideInformation.objects.last()
        self.update_ride(self.driver, ride=ride, status=RideInformation.STARTED)
        ride = RideInformation.objects.get(nk=ride.nk)
        self.assertEqual(RideSerializer(ride).data, client.receive())
