import pytest
from clubs.tests.factories import LeagueDivisionFactory, TeamFactory


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
