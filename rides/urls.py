from django.conf.urls import url
from . import views
from .apis import RideView

urlpatterns = [
    # class based url
    url(r'^all-rides/$', views.RideList.as_view()),
    # function base url
    # url(r'^all-rides/$', views.ride_list),
    #url(r'^all-drivers/$', views.driver_list),
    # url(r'^all-passengers/$', views.passenger_list),
    url(r'^$', RideView.as_view({'get': 'list'}), name='ride_list'),
    url(r'^(?P<ride_nk>\w{32})/$', RideView.as_view({'get': 'retrieve'}), name='ride-details'),
]
