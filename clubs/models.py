from django.db import models
from core.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    league_division = models.ForeignKey(
        "leagues.LeagueDivision",
        on_delete=models.CASCADE,
        related_name="teams",
    )

    def __str__(self):
        return self.name
