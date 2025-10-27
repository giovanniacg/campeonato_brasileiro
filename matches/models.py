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

    def start(self):
        if self.status == Status.IN_PROGRESS:
            raise ValidationError("A partida já está em andamento.")
        if self.status == Status.FINISHED:
            raise ValidationError("A partida já está finalizada.")
        self.status = Status.IN_PROGRESS
        self.save(update_fields=["status"])

    def record_a_goal(self, type: str = "home"):
        if self.status != Status.IN_PROGRESS:
            raise ValidationError(
                "A partida deve estar em andamento para registrar gols."
            )
        if type == "home":
            self.home_score = (self.home_score or 0) + 1
            self.save(update_fields=["home_score"])
        elif type == "away":
            self.away_score = (self.away_score or 0) + 1
            self.save(update_fields=["away_score"])
        else:
            raise ValidationError("Tipo de gol desconhecido. Use 'home' ou 'away'.")

    def finish(self):
        if self.status != Status.IN_PROGRESS:
            raise ValidationError(
                "A partida precisa estar em andamento para ser finalizada."
            )
        self.status = Status.FINISHED
        self.save(update_fields=["status"])
        return self.get_winner()

    def get_winner(self):
        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return None

    def is_draw(self) -> bool:
        return self.home_score == self.away_score

    def cancel(self):
        if self.status == Status.FINISHED:
            raise ValidationError("Não é possível cancelar uma partida já finalizada.")
        self.status = Status.CANCELLED
        self.save(update_fields=["status"])

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["-date"]
