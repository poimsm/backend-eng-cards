from common.models import BaseModel
import uuid
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Device(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE
    )
    objects = models.Manager()


class Profile(BaseModel):
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE
    )
    objects = models.Manager()


class ScreenFlow(BaseModel):
    value = models.CharField(max_length=50, blank=True, null=True)
    time = models.CharField(max_length=50, blank=True, null=True)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE
    )
    objects = models.Manager()
