from rest_framework import serializers

from devices.models import (
    Device, ScreenFlow,
)


class DeviceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'


class ScreenFlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScreenFlow
        fields = '__all__'
