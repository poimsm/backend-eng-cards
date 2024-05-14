from django.urls import re_path
from .views import *

app_name = 'global_settings'

urlpatterns = [
    re_path(r'^check-app-update\/?$', app_update_check_view),
    re_path(r'^check-language-update\/?$', language_update_check_view),
    re_path(r'^available-languages\/?$', languages_list_view),
]
