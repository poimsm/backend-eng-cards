# Python
import logging

# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import transaction

# Serializers
from devices.serializers import (
    DeviceModelSerializer,
    ScreenFlowSerializer,
)

# Custom
from common.decorators import track_and_report

# Services
from devices.services import (
    create_device, get_device_by_id)

logger = logging.getLogger('api_v1')


@api_view(['POST'])
@track_and_report
def screen_flow_create_view(request):
    serializer = ScreenFlowSerializer(data={
        'device': request.data['device_id'],
        'value': request.data['value'],
        'time': request.data['time']
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response([], status=status.HTTP_201_CREATED)


@api_view(['GET'])
@track_and_report
def device_detail_view(request, device_id):
    device = get_device_by_id(device_id)

    if device is None:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'device_id': device.id}, status=status.HTTP_200_OK)


@api_view(['POST'])
@track_and_report
def device_create_view(request):
    device_id = create_device()
    logger.info(f'[{request.request_id}] device_id: {device_id}')
    return Response({'device_id': device_id}, status=status.HTTP_201_CREATED)
