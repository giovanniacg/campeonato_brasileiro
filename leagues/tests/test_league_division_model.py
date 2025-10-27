import pytest
from django.db import IntegrityError
from leagues.tests.factories import LeagueDivisionFactory, LeagueSeasonFactory
from clubs.tests.factories import TeamFactory


@pytest.mark.django_db
def test_create_league_division():
    league_division = LeagueDivisionFactory()
    assert league_division.pk is not None


@pytest.mark.django_db
def test_league_division_parent_league():
    parent_league = LeagueDivisionFactory()
    child_league = LeagueDivisionFactory(parent_league=parent_league)
    assert child_league.parent_league == parent_league


@pytest.mark.django_db
def test_league_division_str_representation():
    league_division = LeagueDivisionFactory(name="Série A")
    assert str(league_division) == "Série A"


@pytest.mark.django_db
def test_league_division_unique_names():
    LeagueDivisionFactory(name="Série B")
    with pytest.raises(IntegrityError):
        LeagueDivisionFactory(name="Série B")


@pytest.mark.django_db
def test_league_division_teams_relationship_zero():
    league_division = LeagueDivisionFactory()
    teams = league_division.teams.all()
    assert teams.count() == 0


@pytest.mark.django_db
def test_league_division_teams_relationship_multiple():
    league_division = LeagueDivisionFactory()
    teams = [TeamFactory(league_division=league_division) for _ in range(3)]
    retrieved_teams = league_division.teams.all()
    assert retrieved_teams.count() == 3
    for team in teams:
        assert team in retrieved_teams


@pytest.mark.django_db
def test_league_division_self_parent():
    league_division = LeagueDivisionFactory()
    league_division.parent_league = league_division
    with pytest.raises(IntegrityError):
        league_division.save()


@pytest.mark.django_db
def test_league_division_season_relationship():
    season = LeagueSeasonFactory(year=2023)
    league_division = LeagueDivisionFactory(season=season)
    assert league_division.season == season


@pytest.mark.django_db
def test_league_division_no_season():
    league_division = LeagueDivisionFactory(season=None)
    assert league_division.season is None


@pytest.mark.django_db
def test_league_division_multiple_creation():
    divisions = LeagueDivisionFactory.create_batch(5)
    assert len(divisions) == 5
    for division in divisions:
        assert division.pk is not None


@pytest.mark.django_db
def test_league_division_multiples_parents_related():
    parent_division = LeagueDivisionFactory()
    LeagueDivisionFactory(parent_league=parent_division)
    with pytest.raises(IntegrityError):
        LeagueDivisionFactory(parent_league=parent_division)
