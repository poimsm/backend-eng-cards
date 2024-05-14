from django.urls import re_path

from .views import *

app_name = 'devices'

urlpatterns = [
    # @app public
    re_path(r'^screen-flow\/?$', screen_flow_create_view),
    re_path(r'^(?P<device_id>[0-9a-f-]+)\/?$', device_detail_view),
    re_path(r'^create\/?$', device_create_view),
]
