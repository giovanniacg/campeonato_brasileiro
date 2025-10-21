from django.db import models
from core.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)


class LeagueDivision(BaseModel):
    name = models.CharField(max_length=100)
    parent_league = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subdivisions",
    )
