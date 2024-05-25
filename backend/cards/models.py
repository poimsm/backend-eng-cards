from django.db import models
from common.models import BaseModel
from devices.models import Device


class Sticker(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    visible = models.BooleanField()
    image_url = models.TextField()
    cover_url = models.TextField()
    objects = models.Manager()


class BasicCard(BaseModel):
    phrase = models.JSONField()
    image_url = models.TextField()
    cover_url = models.TextField()
    voice = models.JSONField(blank=True, null=True)
    visible = models.BooleanField()
    code = models.CharField(max_length=20)
    meaning = models.JSONField(blank=True, null=True)
    examples = models.JSONField(blank=True, null=True)
    scenarios = models.JSONField(blank=True, null=True)
    explanations = models.JSONField(blank=True, null=True)
    vocabs = models.JSONField(blank=True, null=True)
    compare = models.JSONField(blank=True, null=True)
    objects = models.Manager()


class ClusterCard(BaseModel):
    title = models.CharField(max_length=50)
    image_url = models.TextField()
    cover_url = models.TextField()
    code = models.CharField(max_length=20)
    cluster = models.JSONField()
    objects = models.Manager()


class CustomCard(BaseModel):
    phrase = models.JSONField()
    meaning = models.JSONField(blank=True, null=True)
    examples = models.JSONField(blank=True, null=True)
    sticker_code = models.CharField(max_length=20)
    device = models.ForeignKey(
        Device,
        null=True,
        on_delete=models.CASCADE
    )
    objects = models.Manager()


class Category(BaseModel):
    name = models.TextField()
    code = models.CharField(max_length=20)
    cards = models.JSONField(blank=True, null=True)
    basic_cards = models.ManyToManyField(BasicCard)
    cluster_cards = models.ManyToManyField(ClusterCard)
    extras = models.JSONField(blank=True, null=True)
    objects = models.Manager()
