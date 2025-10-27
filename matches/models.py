from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Status(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Agendado"
    IN_PROGRESS = "IN_PROGRESS", "Em andamento"
    FINISHED = "FINISHED", "Finalizado"
    CANCELLED = "CANCELLED", "Cancelado"


class Match(BaseModel):
    home_team = models.ForeignKey(
        "clubs.Team",
        on_delete=models.PROTECT,
        related_name="home_matches",
    )
    away_team = models.ForeignKey(
        "clubs.Team",
        on_delete=models.PROTECT,
        related_name="away_matches",
    )
    league_division = models.ForeignKey(
        "leagues.LeagueDivision",
        on_delete=models.PROTECT,
        related_name="matches",
    )
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

    def clean(self):
        super().clean()
        if (
            self.home_team_id
            and self.away_team_id
            and self.home_team_id == self.away_team_id
        ):
            raise ValidationError("Um time não pode jogar contra si mesmo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["-date"]
