
import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view, renderer_classes
)
from rest_framework.renderers import JSONRenderer

from common.decorators import track_and_report

from global_settings.services import (
    get_mobile_app_info,
    get_languages_info,
    list_languages,
)

logger = logging.getLogger('api_v1')


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@track_and_report
def app_update_check_view(request):
    logger.info(f'[{request.request_id}] fetching app info')
    app_info = get_mobile_app_info()

    data = {
        'update_required': app_info['current_version'] != request.app_version,
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@track_and_report
def language_update_check_view(request):
    lang_version = request.GET.get('lang_version', None)

    logger.info(f'[{request.request_id}] language info')
    lang_info = get_languages_info()

    data = {
        'update_required': lang_info['language_version'] != lang_version,
        'languages': lang_info['languages'],
        'language_version': lang_info['language_version'],
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@track_and_report
def languages_list_view(request):

    logger.info(f'[{request.request_id}] fetching languages')
    languages = list_languages()

    return Response(languages, status=status.HTTP_200_OK)
