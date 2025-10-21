from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
