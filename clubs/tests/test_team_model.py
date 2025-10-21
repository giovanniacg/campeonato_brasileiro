import pytest
from clubs.models import Team
from clubs.tests.factories import TeamFactory


@pytest.mark.django_db
def test_create_team():
    team = TeamFactory()
    assert team.pk is not None
