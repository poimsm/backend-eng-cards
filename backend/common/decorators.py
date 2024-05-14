import functools
import logging
import json

from rest_framework.response import Response
from rest_framework import status
from common.helpers import generate_id

logger = logging.getLogger('api_v1')


def track_and_report(func, log_params=True):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        request_id = generate_id()
        request.request_id = request_id

        logger.info(f'🔵 {func.__name__}')

        if log_params:
            path_params = kwargs
            logger.info(f'[{request_id}] path params: {path_params}')

            try:
                if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    params = json.loads(request.body)
                else:
                    params = request.GET.dict()
            except json.JSONDecodeError:
                params = request.POST.dict()
            except Exception as e:
                logger.critical(f'Error al decodificar parámetros: {str(e)}')
                params = {}

            logger.info(f'[{request_id}] params: {params}')

        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.critical(
                f'[{request_id}] {func.__name__}: {str(e)}', exc_info=True)
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper
