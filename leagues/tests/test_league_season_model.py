import pytest
from leagues.tests.factories import LeagueSeasonFactory


@pytest.mark.django_db
def test_create_league_season():
    league_season = LeagueSeasonFactory()
    assert league_season.pk is not None
