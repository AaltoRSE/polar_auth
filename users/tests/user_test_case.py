from django.test import TestCase
from users.models import User, Subscriber


# TestCases for the user model
class UserTestCase(TestCase):
    def setUp(self):
        # create 2 users
        self.user1_data = {'email': "user1@aalto.fi", "password": "a"}
        self.user2_data = {'email': "user2@aalto.fi", "password": "b"}
        User.objects.create_user(
            self.user1_data['email'],
            self.user1_data['password'],
            is_admin=False, is_staff=False, is_active=True
        )
        User.objects.create_user(
            self.user2_data['email'],
            self.user2_data['password'],
            is_admin=False, is_staff=False, is_active=True
        )
        self.user1 = User.objects.get(email=self.user1_data['email'])
        self.user2 = User.objects.get(email=self.user2_data['email'])

        # create a subscriber
        Subscriber.objects.create(email="user1@aalto.fi")
