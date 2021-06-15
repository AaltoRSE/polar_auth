import uuid

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

        # Create a subject id
        user.user_id = uuid.uuid1().int>>64

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

        # Create a user id
        user.user_id = uuid.uuid1().int>>64

        user.save()
        return user


class User(AbstractUser):
    # Remove the username as a separate field (we use email)
    username = None

    # Require email to be unique
    email = models.EmailField('email address', unique=True,
                              help_text="Email (aalto.fi only)")

    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Also remove the name
    first_name = None
    last_name = None

    # We do need an address to send the device to
    address = models.CharField(
                'address', max_length=50,
                help_text='Address for sending the Polar sport tracker.'
              )

    # Track the three steps that the user needs to complete before they have
    # signed up to the study.
    consent = models.BooleanField('Consented to study', default=False)
    privacy = models.BooleanField('Agreed to privacy notice', default=False)
    first_survey_done = models.BooleanField('Filled first survey', default=False)

    # We use the polar_id to identify the user to the data server.
    # This could, in principle, be identify the user, but we already
    # store the email here in any case.
    polar_id = models.CharField(max_length=20, null=True, blank=True)

    # Before we have access to the polar_id, we need a user ID for the survey
    user_id = models.CharField('ID', max_length=32, blank=True)

    # Set the user manager
    objects = UserManager()

    def ready_to_authorize(self):
        ''' Check if a user is ready to authorize data collection '''
        return self.privacy and self.consent and self.first_survey_done

    def __str__(self):
        return self.email


class Subscriber(models.Model):
    ''' This model only contains an email. Added emails are
    expressions of interest, not actual registrations.'''
    email = models.EmailField(unique=True, help_text="Email (aalto.fi only)")

    def __str__(self):
        return self.email
