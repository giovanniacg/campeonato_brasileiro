from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory.declarations import SubFactory
from clubs.models import LeagueSeason


class LeagueSeasonFactory(DjangoModelFactory):
    class Meta:
        model = LeagueSeason

    year = Faker("year")
    parent_league = None
