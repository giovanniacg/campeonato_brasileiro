from factory.django import DjangoModelFactory
from factory.faker import Faker
from clubs.models import Team


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = Faker("name", locale="pt_BR")
    short_name = Faker("word", locale="pt_BR")
    city = Faker("city", locale="pt_BR")
