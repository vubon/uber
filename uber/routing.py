from channels import route_class
from rides.consumers import DriverConsumer, PassengerConsumer


channel_routing = [
    route_class(DriverConsumer, path=r'^/driver/$'),
    route_class(PassengerConsumer, path=r'^/passenger/$'),
]
