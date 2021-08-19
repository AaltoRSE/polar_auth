from .user_test_case import UserTestCase
from django.urls import reverse
from django.core import mail
from users.models import User
from django.conf import settings
from polar_auth.settings import data_folder


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

    def test_privacy_view(self):
        ''' Check the privacy view redirects to the consent page or the first
            survey
        '''
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # check logged in user can access
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

        # Check default redirect to consent
        response = self.client.post(
            reverse('privacy'), {'privacy': True}
        )
        self.assertRedirects(response, '/consent/')

        # Check redirect to survey
        self.user1.privacy = False
        self.user1.consent = True
        self.user1.save()

        # Check redirect to first survey
        response = self.client.post(
            reverse('privacy'), {'privacy': True}
        )
        # Why 301?
        self.assertRedirects(response, '/surveys/1', target_status_code=301)

        # Check redirect to home
        self.user1.privacy = False
        self.user1.first_survey_done = True
        self.user1.save()

        response = self.client.post(
            reverse('privacy'), {'privacy': True}
        )
        self.assertRedirects(response, '/')

    def test_consent_view(self):
        ''' Check the consent view redirects to privacy consent page or the first
            survey
        '''
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # check logged in user can access
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

        # Check default redirect to consent
        post_data = {
            'field_1': True,
            'field_2': True,
            'field_3': True,
            'field_4': True,
            'field_5': True,
            'field_6': True,
        }
        response = self.client.post(
            reverse('consent'), post_data
        )
        self.assertRedirects(response, '/privacy/')

        # Check redirect to first survey
        self.user1.consent = False
        self.user1.privacy = True
        self.user1.save()

        response = self.client.post(
            reverse('consent'), post_data
        )
        # Why 301?
        self.assertRedirects(response, '/surveys/1', target_status_code=301)

        # Check redirect to home
        self.user1.consent = False
        self.user1.first_survey_done = True
        self.user1.save()

        response = self.client.post(
            reverse('consent'), post_data
        )
        self.assertRedirects(response, '/')

    def test_add_auth_token_view(self):
        with self.settings(data_server=None):
            self.client.login(
                username=self.user1_data['email'],
                password=self.user1_data['password']
            )

            # Count existing tokens
            with open(data_folder + '/new_tokens') as token_file:
                num_lines_at_start = len(token_file.readlines())

            # Post a get
            response = self.client.get(reverse('auth_return'))
            self.assertRedirects(response, reverse('about'))

            # should have sent confirmation email
            self.assertEqual(len(mail.outbox), 1)

            # and added a token to the list of new tokens
            with open(data_folder + '/new_tokens') as token_file:
                lines = token_file.readlines()
                assert(len(lines) == num_lines_at_start+1)
                correct_line = f'debug_token debug_id {self.user1.user_id}\n'
                self.assertEqual(lines[-1], correct_line)



