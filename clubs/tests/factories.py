from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory.declarations import SubFactory
from clubs.models import Team
from clubs.models import LeagueDivision


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = Faker("name", locale="pt_BR")
    league_division = SubFactory("clubs.tests.factories.LeagueDivisionFactory")


class LeagueDivisionFactory(DjangoModelFactory):
    class Meta:
        model = LeagueDivision

    name = Faker("word", locale="pt_BR")
    parent_league = None
