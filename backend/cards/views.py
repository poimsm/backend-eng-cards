# Python
import logging

# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import connections
from django.db.utils import OperationalError

# Models
from cards.models import (
    BasicCard,
    CustomCard,
    ClusterCard,
    Category,
    Sticker,
)

from common.models import Status as StatusModel

# Serializers
from cards.serializers import (
    CustomCardModelSerializer,
    StickerModelSerializer,
)

# Custom
from common.decorators import track_and_report

# Services
from cards.services import (
    get_cluster_card_by_code,
    get_basic_card_by_code,
    get_custom_card_by_id,
    get_sticker_by_code,
    get_cover_basic_card_by_code,
    get_cover_cluster_card_by_code,
)

from devices.services import (
    get_device_by_id,
)

from global_settings.services import (
    get_cards_settings,
)

logger = logging.getLogger('api_v1')


@api_view(['POST'])
@track_and_report
def card_create_view(request):
    device_id = request.data.get('device_id', None)
    phrase = request.data.get('phrase', None)
    meaning = request.data.get('meaning', None)
    sticker_code = request.data.get('sticker_code', None)

    if not phrase or not device_id:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    if get_device_by_id(device_id) is None:
        return Response([], status=status.HTTP_404_NOT_FOUND)

    try:
        Sticker.objects.get(code=sticker_code, status=StatusModel.ACTIVE)
    except Sticker.DoesNotExist:
        return Response([], status=status.HTTP_404_NOT_FOUND)

    serializer = CustomCardModelSerializer(data={
        'phrase': phrase,
        'sticker_code': sticker_code,
        'meaning': meaning,
        'device': device_id,
    })

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({
        'card_id': serializer.data['id']
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@track_and_report
def card_update_view(request):
    card_id = request.data.get('card_id', None)
    device_id = request.data.get('device_id', None)
    phrase = request.data.get('phrase', None)
    meaning = request.data.get('meaning', None)
    sticker_code = request.data.get('sticker_code', None)

    if not all([phrase, meaning, sticker_code, device_id, card_id]):
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    sticker = get_sticker_by_code(sticker_code)

    if sticker is None:
        return Response({'message': 'Sticker Not Found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        card_instance = CustomCard.objects.get(
            id=card_id,
            device_id=device_id
        )
    except CustomCard.DoesNotExist:
        return Response({'message': 'Card Not Found'}, status=status.HTTP_404_NOT_FOUND)

    updated_data = {
        'phrase': phrase,
        'sticker_code': sticker_code,
        'meaning': meaning,
        'device': device_id,
    }

    serializer = CustomCardModelSerializer(
        card_instance, data=updated_data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@track_and_report
def card_delete_view(request):
    card_id = request.data.get('card_id', None)
    device_id = request.data.get('device_id', None)

    if not all([card_id, device_id]):
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    try:
        card_instance = CustomCard.objects.get(
            id=card_id,
            device_id=device_id
        )
    except CustomCard.DoesNotExist:
        return Response([], status=status.HTTP_404_NOT_FOUND)

    updated_data = {
        'status': StatusModel.DELETED,
    }

    serializer = CustomCardModelSerializer(
        card_instance, data=updated_data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@track_and_report
def category_card_list_view(request):
    device_id = request.GET.get('device_id', None)

    if get_device_by_id(device_id) is None:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    category_cards_list = []

    custom_cards = CustomCard.objects.filter(
        device_id=device_id,
        status=StatusModel.ACTIVE
    ).order_by('-id')

    processed_cards = []
    for card in custom_cards:
        sticker = Sticker.objects.get(
            code=card.sticker_code,
            status=StatusModel.ACTIVE
        )
        processed_cards.append({
            'id': card.id,
            'phrase': card.phrase,
            'cover_url': sticker.cover_url
        })

    if len(processed_cards) > 0:
        category_cards_list.append({
            'category': 'Saved',
            'blocks': [{
                'type': 'custom_cards',
                'custom_cards': processed_cards
            }]
        })

    categories = Category.objects.filter(status=StatusModel.ACTIVE)
    card_settings = get_cards_settings()

    sorted_categories = []
    for sort_code in card_settings.extras['category_order']:
        for cat in categories:
            if cat.code == sort_code:
                sorted_categories.append(cat)

    logger.info([cat.name for cat in sorted_categories])

    for category in sorted_categories:
        cat_cards = []
        for cat_item in category.cards:            
            if cat_item['type'] == 'basic_cards':
                basic_cards = []
                for code in cat_item['card_codes']:
                    card = get_cover_basic_card_by_code(code)
                    basic_cards.append(card)
                cat_cards.append({
                    'type': 'basic_cards',
                    'basic_cards': basic_cards
                })

            if cat_item['type'] == 'collections':
                cat_cards.append({
                    'type': 'collections',
                    'collections': cat_item['collections'],
                })

            if cat_item['type'] == 'cluster_cards':
                cluster_cards = []
                for code in cat_item['card_codes']:
                    card = get_cover_cluster_card_by_code(code)
                    cluster_cards.append(card)
                cat_cards.append({
                    'type': 'cluster_cards',
                    'cluster_cards': cluster_cards
                })

        if len(cat_cards) > 0:
            category_cards_list.append({
                'name': category.name,
                'tab_height': category.tab_height,
                'blocks': cat_cards,
            })

    return Response(category_cards_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def card_detail_view(request, identifier):
    card_type = request.GET.get('card_type', None)
    lang_code = request.GET.get('lang', None)
    device_id = request.GET.get('device_id', None)

    try:
        identifier = int(identifier)
        card = get_custom_card_by_id(identifier)
        if card is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(card, status=status.HTTP_200_OK)
    except ValueError:
        if card_type == 'cluster' and lang_code:
            card = get_cluster_card_by_code(identifier, lang_code)
        elif card_type == 'basic' and lang_code:
            card = get_basic_card_by_code(identifier, lang_code)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if card is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(card, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def sticker_list_view(request):
    stickers = Sticker.objects.filter(status=StatusModel.ACTIVE, visible=True)
    serializer = StickerModelSerializer(stickers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def hello_world(request):
    logger.info(request.app_version)
    logger.info(f'request_id: {request.request_id}')
    return Response({
        'hello': 'world!',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def health(request):
    # Verificar la conexión a la base de datos
    # 'default' se refiere a la base de datos predeterminada.
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        # Si hay un error de operación, significa que algo está mal con la base de datos.
        logger.error('Health check failed: Unable to connect to the database.')
        return Response({
            'message': 'Unable to connect to the database.',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Aquí podrías agregar más comprobaciones, como:
    # - Conexión con sistemas de caché
    # - Conexiones a servicios externos (APIs, sistemas de archivos, etc.)
    # - Verificar la disponibilidad de recursos críticos o archivos de configuración

    # Si todo está bien, devolver una respuesta positiva
    logger.info('Health check passed: server up and running')
    return Response({
        'message': 'Server up and running',
    }, status=status.HTTP_200_OK)
