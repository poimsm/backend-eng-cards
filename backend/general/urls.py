from django.urls import path
from .views import policy

app_name = 'general'

urlpatterns = [
    path('policy/', policy, name='policy'),
]
