from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User email missing")
        if not password:
            raise ValueError("User pasword missing")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.is_superuser = is_admin

        # Consent always starts as False
        user.consent = False

        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User email missing")
        if not password:
            raise ValueError("User password missing")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.admin = True
        user.staff = True
        user.active = True
        user.is_superuser = True
        user.consent = False

        user.save()
        return user


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
    consent = models.BooleanField('Consented to study', default=False)

    # Add a field for approving the privacy statement
    privacy = models.BooleanField('Agreed to privacy notice', default=False)

    # We use the polar_id to identify the user to the data server.
    # This could, in principle, be identify the user, but we already
    # store the email here in any case.
    polar_id = models.CharField(max_length=20, null=True, blank=True)

    # Set the user manager
    objects = UserManager()

    def __str__(self):
        return self.email


class Subscriber(models.Model):
    ''' This model only contains an email. Added emails are
    expressions of interest, not actual registrations.'''
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email