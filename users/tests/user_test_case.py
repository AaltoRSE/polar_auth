from django.test import TestCase
from users.models import User, Subscriber


# TestCases for the user model
class UserTestCase(TestCase):
    def setUp(self):
        # create 2 users
        User.objects.create_user("user1@aalto.fi", password="a", is_admin=False, is_staff=False, is_active=True)
        User.objects.create_user("user2@aalto.fi", password="b", is_admin=False, is_staff=False, is_active=True)

        # create a subscriber
        Subscriber.objects.create(email="user1@aalto.fi")
        