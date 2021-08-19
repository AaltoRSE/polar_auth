from .user_test_case import UserTestCase
from django.urls import reverse


class UserViewTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

    def test_user_view(self):
        ''' Check the user view loads with correct logged-in user '''
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        for page in ['', 'consent-success', 'faq']:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['user'], self.user1)
