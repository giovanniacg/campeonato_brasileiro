import pytest
from datetime import timedelta
from django.utils import timezone
from matches.services import FixtureGeneratorService
from matches.models import Match, Status
from clubs.tests.factories import TeamFactory
from leagues.tests.factories import LeagueDivisionFactory, LeagueSeasonFactory


@pytest.mark.django_db
def test_fixture_generator_requires_at_least_two_teams():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    team = TeamFactory()
    division.teams.add(team)

    generator = FixtureGeneratorService(division)

    with pytest.raises(ValueError) as exc_info:
        generator.generate_fixtures()

    assert "pelo menos 2 times" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_fixture_generator_creates_correct_number_of_matches():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    expected_matches = 4 * (4 - 1)
    assert len(matches) == expected_matches


@pytest.mark.django_db
def test_fixture_generator_works_with_odd_number_of_teams():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(5)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    expected_matches = 5 * (5 - 1)
    assert len(matches) == expected_matches


@pytest.mark.django_db
def test_fixture_generator_each_team_plays_all_others_twice():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    for team in teams:
        home_matches = [m for m in matches if m.home_team == team]
        away_matches = [m for m in matches if m.away_team == team]

        assert len(home_matches) == 3
        assert len(away_matches) == 3


@pytest.mark.django_db
def test_fixture_generator_respects_minimum_days_between_matches():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    for team in teams:
        team_matches = sorted(
            [m for m in matches if m.home_team == team or m.away_team == team],
            key=lambda x: x.date,
        )

        for i in range(len(team_matches) - 1):
            days_diff = (team_matches[i + 1].date - team_matches[i].date).days
            assert days_diff >= FixtureGeneratorService.DAYS_BETWEEN_MATCHES


@pytest.mark.django_db
def test_fixture_generator_creates_home_and_away_for_each_pair():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    team1 = TeamFactory(name="Flamengo")
    team2 = TeamFactory(name="Palmeiras")
    division.teams.add(team1, team2)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    home_match = next(
        (m for m in matches if m.home_team == team1 and m.away_team == team2), None
    )
    away_match = next(
        (m for m in matches if m.home_team == team2 and m.away_team == team1), None
    )

    assert home_match is not None
    assert away_match is not None


@pytest.mark.django_db
def test_fixture_generator_all_matches_are_scheduled():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    for match in matches:
        assert match.status == Status.SCHEDULED


@pytest.mark.django_db
def test_fixture_generator_clears_existing_scheduled_matches():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    generator.generate_fixtures()

    generator2 = FixtureGeneratorService(division)
    second_run = generator2.generate_fixtures()

    total_matches = Match.objects.filter(league_division=division).count()
    assert total_matches == len(second_run)


@pytest.mark.django_db
def test_fixture_generator_custom_start_date():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(4)
    division.teams.add(*teams)

    start_date = timezone.now() + timedelta(days=30)
    generator = FixtureGeneratorService(division, start_date=start_date)
    matches = generator.generate_fixtures()

    first_match = min(matches, key=lambda x: x.date)
    assert first_match.date >= start_date


@pytest.mark.django_db
def test_fixture_generator_respects_max_matches_per_day():
    season = LeagueSeasonFactory(year=2024)
    division = LeagueDivisionFactory(season=season)
    teams = TeamFactory.create_batch(6)
    division.teams.add(*teams)

    generator = FixtureGeneratorService(division)
    matches = generator.generate_fixtures()

    matches_by_date = {}
    for match in matches:
        date_key = match.date.date()
        if date_key not in matches_by_date:
            matches_by_date[date_key] = []
        matches_by_date[date_key].append(match)

    for date, day_matches in matches_by_date.items():
        assert len(day_matches) <= FixtureGeneratorService.MAX_MATCHES_PER_DAY
