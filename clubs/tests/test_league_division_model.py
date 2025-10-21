import pytest
from clubs.tests.factories import LeagueDivisionFactory


@pytest.mark.django_db
def test_create_league_division():
    league_division = LeagueDivisionFactory()
    assert league_division.pk is not None


@pytest.mark.django_db
def test_league_division_parent_league():
    parent_league = LeagueDivisionFactory()
    child_league = LeagueDivisionFactory(parent_league=parent_league)
    assert child_league.parent_league == parent_league
