from .user_test_case import UserTestCase
from users.models import User, Subscriber


class UserModelTestCase(UserTestCase):
    def test_user_creation(self):
        user1 = User.objects.get(email="user1@aalto.fi")
        user2 = User.objects.get(email="user2@aalto.fi")

        # Check the email
        self.assertEqual(user1.email, "user1@aalto.fi")

        # The consent, privacy, authorized and first survey fields should
        # be set to false
        self.assertFalse(user1.consent)
        self.assertFalse(user1.privacy)
        self.assertFalse(user1.first_survey_done)

        # Received data, received email and device sent are also False
        self.assertFalse(user1.has_received_email)
        self.assertFalse(user1.device_sent)
        self.assertFalse(user1.received_data)

        # Each user should have an ID
        self.assertNotEqual(user1.user_id, user2.user_id)

        # No username, first name or last name fields
        self.assertIsNone(user1.username)
        self.assertIsNone(user1.first_name)
        self.assertIsNone(user1.last_name)

        # Polar_id is None
        self.assertIsNone(user1.polar_id)

        # The user is not ready to authorize
        self.assertFalse(user1.ready_to_authorize())

        # Finally, __str__ returns the email
        self.assertEqual(str(user1), user1.email)

    def test_susbscriber_creation(self):
        subsriber1 = Subscriber.objects.get(email="user1@aalto.fi")

        # Check the email
        self.assertEqual(subsriber1.email, "user1@aalto.fi")

        # Received data, received email and device sent are also False
        self.assertFalse(subsriber1.has_received_email)

        # __str__ returns the email
        self.assertEqual(str(subsriber1), subsriber1.email)
