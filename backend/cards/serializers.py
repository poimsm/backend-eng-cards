from rest_framework import serializers

from cards.models import (
    CustomCard,
    BasicCard,
    Sticker,
)


class BasicCardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicCard
        fields = '__all__'


class CustomCardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomCard
        fields = '__all__'


class StickerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = '__all__'
