from .user_test_case import UserTestCase
from django.urls import reverse
from django.core import mail
from users.models import User


class UserViewTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

    def test_user_view(self):
        ''' Check the user view loads with correct logged-in user '''
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        for page in ['main', 'consent-success', 'faq']:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['user'], self.user1)

    def test_email_subscribers_view_as_normal_user(self):
        ''' Check the user view loads with correct logged-in user '''
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        response = self.client.get(reverse('email_subscribers'))
        self.assertEqual(response.status_code, 403)

    def test_email_subscribers_view_as_superuser(self):
        ''' Check the user view loads with correct logged-in user
            and email is sent
        '''
        self.client.login(
            username=self.user2_data['email'],
            password=self.user2_data['password']
        )

        response = self.client.get(reverse('email_subscribers'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('email_subscribers'),
            {
             'subject': "This is a test",
             'message': "this is a test",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_view(self):
        ''' Check the view loads for everyone and new user is logged in '''
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

        new_user_pk = User.objects.count() + 1

        response = self.client.post(
            reverse('registration'),
            {
             'email': "user3@aalto.fi",
             'password1': "!Kvc7^eue13g",
             'password2': "!Kvc7^eue13g",
             'has_own_device': True,
             'full_time': True,
             'do_not_foresee_changing_employer': True,
             'will_return_tracker': True,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user_pk)


