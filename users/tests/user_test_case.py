from django.test import TestCase
from users.models import User, Subscriber
from survey.models.survey import Survey
from polar_auth.settings import data_folder
import shutil
import os


# TestCases for the user model
class UserTestCase(TestCase):
    def setUp(self):
        # Delete the test data directory and contents
        shutil.rmtree(data_folder, ignore_errors=True, onerror=None)

        # Create the directory, assuming it's there but empty
        os.mkdir(data_folder)

        # create 2 users
        self.user1_data = {'email': "user1@aalto.fi", "password": "a"}
        self.user2_data = {'email': "user2@aalto.fi", "password": "b"}
        User.objects.create_user(
            self.user1_data['email'],
            self.user1_data['password'],
            is_admin=False, is_staff=False, is_active=True
        )
        User.objects.create_superuser(
            self.user2_data['email'],
            self.user2_data['password']
        )
        self.user1 = User.objects.get(email=self.user1_data['email'])
        self.user2 = User.objects.get(email=self.user2_data['email'])

        # create a subscriber
        Subscriber.objects.create(email="user1@aalto.fi")

        # Create an initial survey
        Survey.objects.create(
            name="name",
            description="description",
            need_logged_user=True
        )

    def TearDown(self):
        # Delete the test data directory and contents
        shutil.rmtree(data_folder, ignore_errors=False, onerror=None)
