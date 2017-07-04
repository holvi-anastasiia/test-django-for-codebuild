from django.db import models


class TestModel(models.Model):
    """
    Model for testing object creation in docker
    """
    title = models.CharField(
        max_length=255, null=True, blank=True)