from django.db import models
from core.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
