from factory.django import DjangoModelFactory
from factory.faker import Faker
from leagues.models import LeagueSeason, LeagueDivision


class LeagueSeasonFactory(DjangoModelFactory):
    class Meta:
        model = LeagueSeason

    year = Faker("year")
    parent_league = None


class LeagueDivisionFactory(DjangoModelFactory):
    class Meta:
        model = LeagueDivision

    name = Faker("word", locale="pt_BR")
    parent_league = None
