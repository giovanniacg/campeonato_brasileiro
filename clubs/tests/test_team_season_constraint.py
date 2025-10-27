import pytest
from django.core.exceptions import ValidationError
from clubs.tests.factories import TeamFactory
from leagues.tests.factories import LeagueSeasonFactory, LeagueDivisionFactory


@pytest.mark.django_db
def test_team_can_be_in_one_division_per_season():
    """
    Testa que um time pode estar em uma divisão por season.
    """
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season, name="Série A 2024")
    team = TeamFactory(name="Flamengo")

    # Adiciona o time à divisão
    division.teams.add(team)

    # Valida que não há erro
    team.full_clean()
    assert team in division.teams.all()


@pytest.mark.django_db
def test_team_cannot_be_in_multiple_divisions_same_season():
    """
    Testa que um time NÃO pode estar em múltiplas divisões da mesma season.
    """
    season = LeagueSeasonFactory(year=2024)
    division_a = LeagueDivisionFactory(season=season, name="Série A 2024")
    division_b = LeagueDivisionFactory(season=season, name="Série B 2024")
    team = TeamFactory(name="Palmeiras")

    # Adiciona o time à primeira divisão
    division_a.teams.add(team)
    team.refresh_from_db()
    team.full_clean()  # OK

    # Tenta adicionar à segunda divisão da mesma season
    division_b.teams.add(team)
    team.refresh_from_db()

    # Deve lançar ValidationError
    with pytest.raises(ValidationError) as exc_info:
        team.full_clean()

    assert "já está registrado em outra divisão" in str(exc_info.value)


@pytest.mark.django_db
def test_team_can_be_in_different_seasons():
    """
    Testa que um time PODE estar em divisões de seasons diferentes.
    """
    season_2024 = LeagueSeasonFactory(year=2024)
    season_2025 = LeagueSeasonFactory(year=2025)

    division_2024 = LeagueDivisionFactory(season=season_2024, name="Série A 2024")
    division_2025 = LeagueDivisionFactory(season=season_2025, name="Série A 2025")

    team = TeamFactory(name="São Paulo")

    # Adiciona em ambas as divisões (seasons diferentes)
    division_2024.teams.add(team)
    division_2025.teams.add(team)

    team.refresh_from_db()

    # Deve passar a validação
    team.full_clean()

    assert team in division_2024.teams.all()
    assert team in division_2025.teams.all()
