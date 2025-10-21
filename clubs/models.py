from django.db import models
from core.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LeagueDivision(BaseModel):
    name = models.CharField(max_length=100)
    parent_league = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subdivisions",
    )
