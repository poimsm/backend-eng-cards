# from django.conf import settings
import logging
from django.http import HttpResponseBadRequest

log = logging.getLogger('api_v1')


class AppVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/general/'):
            return self.get_response(request)
        
        version = request.headers.get('App-Version')
        if not version:
            return HttpResponseBadRequest("APP version is required.")

        request.app_version = version
        response = self.get_response(request)
        return response
