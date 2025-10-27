import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
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
    teams = [TeamFactory() for _ in range(3)]
    league_division.teams.set(teams)
    retrieved_teams = league_division.teams.all()
    assert retrieved_teams.count() == 3
    for team in teams:
        assert team in retrieved_teams


@pytest.mark.django_db
def test_team_division_retrieval():
    league_division = LeagueDivisionFactory(name="Série C")
    team = TeamFactory()
    league_division.teams.add(team)
    retrieved_division = team.league_divisions.first()
    assert retrieved_division == league_division


@pytest.mark.django_db
def test_team_multiple_divisions_in_same_season():
    season = LeagueSeasonFactory(year=2023)
    league_division1 = LeagueDivisionFactory(name="Série A 2023", season=season)
    league_division2 = LeagueDivisionFactory(name="Série B 2023", season=season)
    team = TeamFactory()
    league_division1.teams.add(team)
    league_division2.teams.add(team)
    team.refresh_from_db()

    with pytest.raises(ValidationError) as exc_info:
        team.full_clean()

    assert "já está registrado em outra divisão" in str(exc_info.value)


@pytest.mark.django_db
def test_team_multiple_divisions_in_different_seasons():
    season1 = LeagueSeasonFactory(year=2022)
    season2 = LeagueSeasonFactory(year=2023)
    league_division1 = LeagueDivisionFactory(name="Série A 2022", season=season1)
    league_division2 = LeagueDivisionFactory(name="Série A 2023", season=season2)
    team = TeamFactory()
    league_division1.teams.add(team)
    league_division2.teams.add(team)
    team.refresh_from_db()

    team.full_clean()

    assert team in league_division1.teams.all()
    assert team in league_division2.teams.all()


@pytest.mark.django_db
def test_league_division_self_parent():
    league_division = LeagueDivisionFactory()
    league_division.parent_league = league_division
    with pytest.raises(Exception):
        league_division.save()


@pytest.mark.django_db
def test_league_division_season_relationship():
    season = LeagueSeasonFactory(year=2023)
    league_division = LeagueDivisionFactory(season=season)
    assert league_division.season == season


@pytest.mark.django_db
def test_league_division_no_season():
    with pytest.raises(IntegrityError):
        LeagueDivisionFactory(season=None)


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
