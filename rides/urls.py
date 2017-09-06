from django.conf.urls import url
# from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # class based url
    url(r'^all-rides/$', views.RideList.as_view()),
    # function base url
    # url(r'^all-rides/$', views.ride_list),
    url(r'^all-drivers/$', views.driver_list),
    url(r'^all-passengers/$', views.passenger_list),
]
# urlpatterns = format_suffix_patterns(urlpatterns)