from factory.django import DjangoModelFactory
from factory.declarations import SubFactory, Sequence
from leagues.models import LeagueSeason, LeagueDivision


class LeagueSeasonFactory(DjangoModelFactory):
    class Meta:
        model = LeagueSeason

    year = Sequence(lambda n: 2000 + n)
    parent_league = None


class LeagueDivisionFactory(DjangoModelFactory):
    class Meta:
        model = LeagueDivision

    name = Sequence(lambda n: f"Divisão {n}")
    parent_league = None
    season = SubFactory(LeagueSeasonFactory)
