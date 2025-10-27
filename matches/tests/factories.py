from factory.django import DjangoModelFactory
from factory.declarations import SubFactory, LazyFunction
from django.utils import timezone
from datetime import timedelta
from matches.models import Match, Status


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    date = LazyFunction(lambda: timezone.now() + timedelta(days=7))
    status = Status.SCHEDULED
    home_team = SubFactory("clubs.tests.factories.TeamFactory")
    away_team = SubFactory("clubs.tests.factories.TeamFactory")
    league_division = SubFactory("leagues.tests.factories.LeagueDivisionFactory")
    home_score = 0
    away_score = 0
