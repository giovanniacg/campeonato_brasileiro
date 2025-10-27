from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def clean(self):
        """
        Valida que o time não está em múltiplas divisões da mesma season.
        Esta validação é executada antes do save quando full_clean() é chamado.
        """
        super().clean()

        if self.pk:
            # Obtém todas as divisões em que este time participa
            divisions = self.league_divisions.select_related("season").all()

            # Agrupa por season e verifica duplicatas
            seasons_count = {}
            for division in divisions:
                season_id = division.season_id
                if season_id in seasons_count:
                    raise ValidationError(
                        f"O time '{self.name}' já está registrado em outra divisão "
                        f"da temporada {division.season.year}."
                    )
                seasons_count[season_id] = division
