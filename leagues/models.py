from core.models import BaseModel
from django.db import models


class LeagueSeason(BaseModel):
    year = models.PositiveIntegerField(unique=True)
    parent_league = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subseason",
    )
