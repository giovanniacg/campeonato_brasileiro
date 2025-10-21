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

    def __str__(self) -> str:
        return f"{self.year}"

    def save(self, *args, **kwargs):
        if self.parent_league and self.parent_league.pk == self.pk:
            raise ValueError("Uma liga não pode ser seu próprio ancestral.")
        super().save(*args, **kwargs)
