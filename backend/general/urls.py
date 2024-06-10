from django.urls import re_path
from .views import policy, delete

app_name = 'general'

urlpatterns = [
    re_path(r'^policy\/?$', policy, name='policy'),
    re_path(r'^how-to-delete-account\/?$', delete, name='delete'),
]
