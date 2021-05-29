from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):

    # We use the polar_id to identify the user to the data server.
    # This could, in principle, be identify the user, but we already
    # store the email here in any case.
    polar_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.email
