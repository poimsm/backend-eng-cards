from django.urls import re_path

from .views import *

app_name = 'cards'

urlpatterns = [
    # @app public
    re_path(r'^(?P<card_id>\d+)/?$', card_detail_view),
    re_path(r'^create\/?$', card_create_view),
    re_path(r'^update\/?$', card_update_view),
    re_path(r'^delete\/?$', card_delete_view),
    re_path(r'^find-id\/?$', find_card_id),
    re_path(r'^category-cards\/?$', category_card_list_view),
    re_path(r'^stickers\/?$', sticker_list_view),
    re_path(r'^hola\/?$', hello_world),
]
