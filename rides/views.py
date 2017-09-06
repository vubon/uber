from django.shortcuts import render
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import RideInformation, Driver, Passenger
from .serializers import RideSerializer, DriverSerializer, PassengerSerializer

# Create your views here.


class RideList(APIView):
    """
    List all rides, or create a new ride.
    """
    def get(self, request, format=None):
        ride_information = RideInformation.objects.all()
        serializer = RideSerializer(ride_information, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RideSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'POST'])
# def ride_list(request):
#     """
#     List all rides, or create a new ride.
#     """
#     if request.method == 'GET':
#         ride_information = RideInformation.objects.all()
#         serializer = RideSerializer(ride_information, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = RideSerializer(data=request.data)
#         print(serializer)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def driver_list(request):
    if request.method == 'GET':
        drivers = Driver.objects.all()
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def passenger_list(request):
    if request.method == 'GET':
        passenger = Passenger.objects.all()
        serializer = PassengerSerializer(passenger, many=True)
        return Response(serializer.data)