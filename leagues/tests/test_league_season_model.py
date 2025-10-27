import pytest
from leagues.tests.factories import LeagueSeasonFactory


@pytest.mark.django_db
def test_create_league_season():
    league_season = LeagueSeasonFactory()
    assert league_season.pk is not None


@pytest.mark.django_db
def test_league_season_str_representation():
    league_season = LeagueSeasonFactory(year="2023")
    assert str(league_season) == "2023"


@pytest.mark.django_db
def test_league_season_unique_years():
    LeagueSeasonFactory(year=2022)
    with pytest.raises(Exception):
        LeagueSeasonFactory(year=2022)


@pytest.mark.django_db
def test_league_season_parent_league():
    parent_season = LeagueSeasonFactory(year=2021)
    child_season = LeagueSeasonFactory(year=2022, parent_league=parent_season)
    assert child_season.parent_league == parent_season


@pytest.mark.django_db
def test_league_season_no_parent_league():
    league_season = LeagueSeasonFactory(year=2020, parent_league=None)
    assert league_season.parent_league is None


@pytest.mark.django_db
def test_league_season_self_parent():
    league_season = LeagueSeasonFactory(year=2019)
    league_season.parent_league = league_season
    with pytest.raises(Exception):
        league_season.save()


@pytest.mark.django_db
def test_league_season_multiple_creation():
    seasons = LeagueSeasonFactory.create_batch(5)
    assert len(seasons) == 5
    for season in seasons:
        assert season.pk is not None


@pytest.mark.django_db
def test_league_season_year_negative():
    with pytest.raises(Exception):
        LeagueSeasonFactory(year=-2021)


@pytest.mark.django_db
def test_league_season_multiples_parents_related():
    parent_season = LeagueSeasonFactory(year=2018)
    child_season1 = LeagueSeasonFactory(year=2019, parent_league=parent_season)
    assert child_season1.parent_league == parent_season
    with pytest.raises(Exception):
        LeagueSeasonFactory(year=2020, parent_league=parent_season)
