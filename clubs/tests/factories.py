from factory.django import DjangoModelFactory
from factory.faker import Faker
from clubs.models import Team
from clubs.models import LeagueDivision


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = Faker("name", locale="pt_BR")
    short_name = Faker("word", locale="pt_BR")
    city = Faker("city", locale="pt_BR")


class LeagueDivisionFactory(DjangoModelFactory):
    class Meta:
        model = LeagueDivision

    name = Faker("word", locale="pt_BR")
    parent_league = None
