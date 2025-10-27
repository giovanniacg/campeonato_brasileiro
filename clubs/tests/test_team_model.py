import pytest
from django.db import IntegrityError
from clubs.tests.factories import TeamFactory


@pytest.mark.django_db
def test_create_team():
    team = TeamFactory()
    assert team.pk is not None


@pytest.mark.django_db
def test_team_str_representation():
    team = TeamFactory(name="Clube de Regatas do Flamengo")
    assert str(team) == "Clube de Regatas do Flamengo"


@pytest.mark.django_db
def test_multiple_teams_creation():
    teams = TeamFactory.create_batch(5)
    assert len(teams) == 5
    for team in teams:
        assert team.pk is not None


@pytest.mark.django_db
def test_team_unique_names():
    TeamFactory(name="Palmeiras")
    with pytest.raises(IntegrityError):
        TeamFactory(name="Palmeiras")
