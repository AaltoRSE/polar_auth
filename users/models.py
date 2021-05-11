from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    oauth2_token = models.CharField(max_length=20, null=True, blank=True)
    polar_id = models.CharField(max_length=20, null=True, blank=True)
    access_token = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.email
