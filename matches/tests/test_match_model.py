import pytest
from django.core.exceptions import ValidationError
from matches.tests.factories import MatchFactory
from matches.models import Status
from clubs.tests.factories import TeamFactory


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
def test_match_cannot_have_same_home_and_away_team():
    team = TeamFactory(name="Flamengo")
    match = MatchFactory.build(home_team=team, away_team=team)
    with pytest.raises(ValidationError) as exc_info:
        match.full_clean()
    assert "si mesmo" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_start_partida():
    match = MatchFactory(status=Status.SCHEDULED)
    match.start()

    assert match.status == Status.IN_PROGRESS


@pytest.mark.django_db
def test_match_cannot_start_if_already_started():
    match = MatchFactory(status=Status.IN_PROGRESS)

    with pytest.raises(ValidationError) as exc_info:
        match.start()

    assert "já está em andamento" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_cannot_start_if_finished():
    match = MatchFactory(status=Status.FINISHED, home_score=2, away_score=1)

    with pytest.raises(ValidationError) as exc_info:
        match.start()

    assert "finalizada" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_record_a_goal_home():
    match = MatchFactory(status=Status.IN_PROGRESS)
    match.record_a_goal(type="home")

    assert match.home_score == 1
    assert match.away_score == 0


@pytest.mark.django_db
def test_match_record_a_goal_away():
    match = MatchFactory(status=Status.IN_PROGRESS)
    match.record_a_goal(type="away")

    assert match.home_score == 0
    assert match.away_score == 1


@pytest.mark.django_db
def test_match_registrar_multiplos_gols():
    match = MatchFactory(status=Status.IN_PROGRESS)
    match.record_a_goal(type="home")
    match.record_a_goal(type="home")
    match.record_a_goal(type="away")

    assert match.home_score == 2
    assert match.away_score == 1


@pytest.mark.django_db
def test_match_cannot_record_a_goal_if_not_in_progress():
    match = MatchFactory(status=Status.SCHEDULED)

    with pytest.raises(ValidationError) as exc_info:
        match.record_a_goal(type="home")

    assert "em andamento" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_finish_com_winner_home():
    match = MatchFactory(status=Status.IN_PROGRESS, home_score=3, away_score=1)
    winner = match.finish()

    assert match.status == Status.FINISHED
    assert winner == match.home_team


@pytest.mark.django_db
def test_match_finish_com_winner_away():
    match = MatchFactory(status=Status.IN_PROGRESS, home_score=1, away_score=2)
    winner = match.finish()

    assert match.status == Status.FINISHED
    assert winner == match.away_team


@pytest.mark.django_db
def test_match_finish_com_draw():
    match = MatchFactory(status=Status.IN_PROGRESS, home_score=2, away_score=2)
    winner = match.finish()

    assert match.status == Status.FINISHED
    assert winner is None


@pytest.mark.django_db
def test_match_cannot_finish_if_not_in_progress():
    match = MatchFactory(status=Status.SCHEDULED)

    with pytest.raises(ValidationError) as exc_info:
        match.finish()

    assert "em andamento" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_get_winner_home_win():
    match = MatchFactory(status=Status.FINISHED, home_score=3, away_score=1)

    assert match.get_winner() == match.home_team


@pytest.mark.django_db
def test_match_get_winner_away_win():
    match = MatchFactory(status=Status.FINISHED, home_score=0, away_score=2)

    assert match.get_winner() == match.away_team


@pytest.mark.django_db
def test_match_get_winner_draw():
    match = MatchFactory(status=Status.FINISHED, home_score=1, away_score=1)

    assert match.get_winner() is None


@pytest.mark.django_db
def test_match_is_draw():
    match = MatchFactory(status=Status.FINISHED, home_score=2, away_score=2)

    assert match.is_draw() is True


@pytest.mark.django_db
def test_match_is_not_draw():
    match = MatchFactory(status=Status.FINISHED, home_score=3, away_score=1)

    assert match.is_draw() is False


@pytest.mark.django_db
def test_match_cancel():
    match = MatchFactory(status=Status.SCHEDULED)
    match.cancel()

    assert match.status == Status.CANCELLED


@pytest.mark.django_db
def test_match_cannot_cancel_if_finished():
    match = MatchFactory(status=Status.FINISHED, home_score=2, away_score=1)

    with pytest.raises(ValidationError) as exc_info:
        match.cancel()

    assert "finalizada" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_calculate_points_home_win():
    match = MatchFactory(status=Status.FINISHED, home_score=3, away_score=1)
    home_points, away_points = match.calculate_points()

    assert home_points == 3
    assert away_points == 0


@pytest.mark.django_db
def test_match_calculate_points_away_win():
    match = MatchFactory(status=Status.FINISHED, home_score=1, away_score=2)
    home_points, away_points = match.calculate_points()

    assert home_points == 0
    assert away_points == 3


@pytest.mark.django_db
def test_match_calculate_points_draw():
    match = MatchFactory(status=Status.FINISHED, home_score=2, away_score=2)
    home_points, away_points = match.calculate_points()

    assert home_points == 1
    assert away_points == 1


@pytest.mark.django_db
def test_match_calculate_points_only_for_finished():
    match = MatchFactory(status=Status.IN_PROGRESS, home_score=2, away_score=1)

    with pytest.raises(ValidationError) as exc_info:
        match.calculate_points()

    assert "finalizada" in str(exc_info.value).lower()


@pytest.mark.django_db
def test_match_calculate_points_zero_zero_draw():
    match = MatchFactory(status=Status.FINISHED, home_score=0, away_score=0)
    home_points, away_points = match.calculate_points()

    assert home_points == 1
    assert away_points == 1
