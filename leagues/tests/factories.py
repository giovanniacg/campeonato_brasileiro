from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory.declarations import SubFactory
from leagues.models import LeagueSeason


class LeagueSeasonFactory(DjangoModelFactory):
    class Meta:
        model = LeagueSeason

    year = Faker("year")
    parent_league = None
