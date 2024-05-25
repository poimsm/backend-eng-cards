# Python
import logging

# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import transaction
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
    get_english_text,
    get_cluster_card,
    get_basic_card,
    get_custom_card,
    get_sticker_by_code,
)

from devices.services import (
    get_device_by_id,
)

from global_settings.services import (
    get_card_settings,
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
            'cover_url': sticker.cover_url,
            'type': 'custom'
        })

    if len(processed_cards) > 0:
        category_cards_list.append({
            'category': 'Saved',
            'cards': processed_cards
        })

    categories = Category.objects.filter(status=StatusModel.ACTIVE)
    card_settings = get_card_settings()

    sorted_categories = []
    for sort_code in card_settings.extras['category_order']:
        for cat in categories:
            if cat.code == sort_code:
                sorted_categories.append(cat)

    for category in sorted_categories:
        basic_cards = BasicCard.objects.filter(
            category=category, visible=True)
        processed_cards = []

        if category.extras and category.extras.get('basic_card_order'):
            for code in category.extras.get('basic_card_order'):
                processed_cards = [{
                    'id': card.id,
                    'code': card.code,
                    'phrase': get_english_text(card.phrase),
                    'cover_url': card.cover_url,
                    'type': 'basic'
                } for card in basic_cards.filter(code__in=code)]

                if len(processed_cards) > 0:
                    cluster_cards = ClusterCard.objects.filter(
                        category=category)
                    processed_cluster_cards = [{
                        'id': card.id,
                        'code': card.code,
                        'cover_url': card.cover_url,
                        'type': 'cluster'
                    } for card in cluster_cards]
                    category_cards_list.append({
                        'category': category.name,
                        'cards': processed_cards,
                        'cluster_cards': processed_cluster_cards
                    })
        else:
            processed_cards = [{
                'id': card.id,
                'code': card.code,
                'phrase': get_english_text(card.phrase),
                'cover_url': card.cover_url,
                'type': 'basic'
            } for card in basic_cards]

            if len(processed_cards) > 0:
                cluster_cards = ClusterCard.objects.filter(
                    category=category)
                processed_cluster_cards = [{
                    'id': card.id,
                    'code': card.code,
                    'cover_url': card.cover_url,
                    'type': 'cluster'
                } for card in cluster_cards]
                category_cards_list.append({
                    'category': category.name,
                    'cards': processed_cards,
                    'cluster_cards': processed_cluster_cards
                })

    return Response(category_cards_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def card_detail_view(request, card_id):
    card_type = request.GET.get('card_type', None)
    lang_code = request.GET.get('lang', None)
    device_id = request.GET.get('device_id', None)

    card = None

    if card_type == 'basic' and lang_code:
        card = get_basic_card(card_id, lang_code)

    if card_type == 'cluster' and lang_code:
        card = get_cluster_card(card_id, lang_code)

    if card_type == 'custom' and device_id:
        card = get_custom_card(card_id)

    if not card:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(card, status=status.HTTP_200_OK)


@api_view(['GET'])
@track_and_report
def find_card_id(request):
    card_code = request.GET.get('card_code', None)

    try:
        card = BasicCard.objects.get(
            code=card_code,
            status=StatusModel.ACTIVE,
        )
    except BasicCard.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(card.id, status=status.HTTP_200_OK)


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
