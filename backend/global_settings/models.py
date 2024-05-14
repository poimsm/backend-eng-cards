from common.models import BaseModel
from django.db import models


class GlobalSetting(BaseModel):
    type = models.TextField()
    notes = models.TextField(blank=True, null=True)
    extras = models.JSONField(blank=True, null=True)
    objects = models.Manager()
