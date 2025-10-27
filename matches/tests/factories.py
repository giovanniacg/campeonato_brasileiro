from factory.django import DjangoModelFactory
from factory.declarations import SubFactory
from datetime import datetime
from matches.models import Match, Status


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    date = datetime(2024, 1, 1)
    status = Status.SCHEDULED
    home_team = SubFactory("clubs.tests.factories.TeamFactory")
    away_team = SubFactory("clubs.tests.factories.TeamFactory")
    league_division = SubFactory("leagues.tests.factories.LeagueDivisionFactory")
    home_score = 0
    away_score = 0
