from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    # Remove the username as a separate field (we use email)
    username = None

    # Require email to be unique
    email = models.EmailField('email address', unique=True)

    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Also remove the name
    first_name = None
    last_name = None

    # Add a field for consent
    consent = models.BooleanField('consent')

    # We use the polar_id to identify the user to the data server.
    # This could, in principle, be identify the user, but we already
    # store the email here in any case.
    polar_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.email
