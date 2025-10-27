import pytest
from django.core.exceptions import ValidationError
from matches.tests.factories import MatchFactory
from clubs.tests.factories import TeamFactory
from leagues.tests.factories import LeagueDivisionFactory


@pytest.mark.django_db
def test_create_match():
    match = MatchFactory()
    assert match.pk is not None


@pytest.mark.django_db
def test_match_str_representation():
    home_team = TeamFactory(name="Flamengo")
    away_team = TeamFactory(name="Palmeiras")
    match = MatchFactory(home_team=home_team, away_team=away_team)
    assert str(match) == "Flamengo vs Palmeiras"


@pytest.mark.django_db
def test_match_has_home_team():
    home_team = TeamFactory(name="Corinthians")
    match = MatchFactory(home_team=home_team)
    assert match.home_team == home_team


@pytest.mark.django_db
def test_match_has_away_team():
    away_team = TeamFactory(name="São Paulo")
    match = MatchFactory(away_team=away_team)
    assert match.away_team == away_team


@pytest.mark.django_db
def test_match_has_league_division():
    division = LeagueDivisionFactory(name="Série A")
    match = MatchFactory(league_division=division)
    assert match.league_division == division


@pytest.mark.django_db
def test_match_has_date():
    match = MatchFactory()
    assert match.date is not None


@pytest.mark.django_db
def test_match_has_status():
    match = MatchFactory()
    assert match.status is not None


@pytest.mark.django_db
def test_match_initial_scores_are_zero():
    match = MatchFactory()
    assert match.home_score == 0
    assert match.away_score == 0


@pytest.mark.django_db
def test_match_can_update_scores():
    match = MatchFactory()
    match.home_score = 2
    match.away_score = 1
    match.save()
    match.refresh_from_db()
    assert match.home_score == 2
    assert match.away_score == 1


@pytest.mark.django_db
def test_match_cannot_have_same_home_and_away_team():
    team = TeamFactory(name="Flamengo")
    match = MatchFactory.build(home_team=team, away_team=team)
    with pytest.raises(ValidationError) as exc_info:
        match.full_clean()
    assert "mesmo time" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_multiple_matches_creation():
    matches = MatchFactory.create_batch(5)
    assert len(matches) == 5
    for match in matches:
        assert match.pk is not None
