from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory.declarations import SubFactory
from clubs.models import Team


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = Faker("name", locale="pt_BR")
    league_division = SubFactory("clubs.tests.factories.LeagueDivisionFactory")
