from .user_test_case import UserTestCase
from users.models import User, Subscriber
from django.core import mail
from polar_auth.settings import data_folder
import users.forms as forms


class UserRegisterFormTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        # Correct data for the form
        self.data = {
            "email": "user3@aalto.fi",
            "has_own_device": True,
            "full_time": True,
            "do_not_foresee_changing_employer": True,
            "will_return_tracker": True,
            "password1": "1Xx7*4&ZFNNM",
            "password2": "1Xx7*4&ZFNNM",
        }

    def check_error_with_field_false(self, field_name):
        ''' Check that a form fails when given field is false '''
        # Fill in the data and create initialize form
        self.data[field_name] = False
        form = forms.UserRegisterForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn(field_name, form.errors.keys())

    def test_with_own_device(self):
        ''' Check with valid data. '''
        # Fill in the data and create initialize form
        form = forms.UserRegisterForm(data=self.data)

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Check that saving the form adds to the database
        form.save()
        user = User.objects.get(email="user3@aalto.fi")
        self.assertEqual(user.email, "user3@aalto.fi")

    def test_with_no_device(self):
        ''' Should fail if the user does not have a device '''
        # Fill in the data and create initialize form
        self.data["has_own_device"] = False
        form = forms.UserRegisterForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.non_field_errors()) > 0)

    def test_without_full_time(self):
        ''' Should fail if the user is not full time '''
        self.check_error_with_field_false("full_time")

    def test_foresee_changing_jobs(self):
        ''' should fail if the user expect to change jobs '''
        self.check_error_with_field_false("do_not_foresee_changing_employer")

    def test_will_return_tracker(self):
        ''' should fail if the user does not promise to return the tracker '''
        self.check_error_with_field_false("will_return_tracker")

    def test_with_no_email(self):
        ''' Fail if email is not provided '''
        # Fill in the data and create initialize form
        self.data["email"] = ""
        form = forms.UserRegisterForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors.keys())

    def test_with_non_aalto_email(self):
        ''' Fail if the email is not under Aalto domain. '''
        # Fill in the data and create initialize form
        self.data["email"] = "user@example.com"
        form = forms.UserRegisterForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors.keys())


class UserPrivacyFormTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        # Correct data for the form
        self.data = {"privacy": True}

    def test_without_agreement(self):
        ''' Should fail the user does not agree '''
        # Fill in the data and create initialize form
        self.data['privacy'] = False
        form = forms.PrivacyForm(data=self.data)
        form.instance = User.objects.get(email="user1@aalto.fi")

        # Check that the form is valid
        self.assertFalse(form.is_valid())
        self.assertIn('privacy', form.errors.keys())

    def validate_and_save_form(self, user):
        ''' Validate and save with valid data. '''
        # Fill in the data and create initialize form
        form = forms.PrivacyForm(data=self.data)
        form.instance = user

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Check that saving the form adds to the database
        form.save()
        user = User.objects.get(email=user.email)
        self.assertTrue(user.privacy)

    def test_no_consent(self):
        ''' User has not consented -> no email '''
        user = User.objects.get(email="user1@aalto.fi")
        for consent, survey in [(False, False), (True, False), (False, True)]:
            user.consent = consent
            user.first_survey_done = survey
            user.save()
            self.validate_and_save_form(user)

            # Check that no email has been sent
            self.assertEqual(len(mail.outbox), 0)

    def test_with_survey_and_consent(self):
        ''' User has consented and filled the survey -> send email '''
        user = User.objects.get(email="user1@aalto.fi")
        user.consent = True
        user.first_survey_done = True
        user.save()
        self.validate_and_save_form(user)

        # Check that the email has been sent
        self.assertEqual(len(mail.outbox), 1)


class UserConsentFormTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        # Correct data for the form
        self.data = {
            "field_1": True,
            "field_2": True,
            "field_3": True,
            "field_4": True,
            "field_5": True,
            "field_6": True,
        }

    def test_with_missing_field(self):
        ''' Should fail the user does not agree to all points '''
        # Fill in the data and create initialize form
        for i in range(1, 7):
            field_name = f"field_{i}"
            self.data[field_name] = False
            form = forms.ConsentForm(data=self.data)
            form.instance = User.objects.get(email="user1@aalto.fi")

            # Check that the form is valid
            self.assertFalse(form.is_valid())
            self.assertIn(field_name, form.errors.keys())

    def validate_and_save_form(self, user):
        ''' Validate and save with valid data. '''
        # Fill in the data and create initialize form
        form = forms.ConsentForm(data=self.data)
        form.instance = user

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Check that saving the form adds to the database
        form.save()
        user = User.objects.get(email=user.email)
        self.assertTrue(user.consent)

    def test_no_privacy_or_survey(self):
        ''' User has filled the privacy form -> no email '''
        user = User.objects.get(email="user1@aalto.fi")
        for privacy, survey in [(False, False), (True, False), (False, True)]:
            user.privacy = privacy
            user.first_survey_done = survey
            user.save()
            self.validate_and_save_form(user)

            # Check that no email has been sent
            self.assertEqual(len(mail.outbox), 0)

    def test_with_survey_and_privacy(self):
        ''' User has filled the privacy form and the survey -> send email '''
        user = User.objects.get(email="user1@aalto.fi")
        user.privacy = True
        user.first_survey_done = True
        user.save()
        self.validate_and_save_form(user)

        # Check that the email has been sent
        self.assertEqual(len(mail.outbox), 1)


class SubscriptionFormTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        # Correct data for the form
        self.data = {"email": "user3@aalto.fi"}

    def test_valid(self):
        ''' Check with valid data. '''
        # Fill in the data and create initialize form
        form = forms.SubscriptionForm(data=self.data)

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Check that saving the form adds to the database
        form.save()
        subscriber = Subscriber.objects.get(email="user3@aalto.fi")
        self.assertEqual(subscriber.email, "user3@aalto.fi")

    def test_with_no_email(self):
        ''' Fail if email is not provided '''
        # Fill in the data and create initialize form
        self.data["email"] = ""
        form = forms.SubscriptionForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors.keys())

    def test_with_non_aalto_email(self):
        ''' Fail if the email is not under Aalto domain. '''
        # Fill in the data and create initialize form
        self.data["email"] = "user@example.com"
        form = forms.SubscriptionForm(data=self.data)

        # Check that the form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors.keys())


class RemoveAuthorizationFormTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

        # Correct data for the form
        self.data = {"Remove_authorization": True}

    def test_valid(self):
        ''' Check with valid data. '''
        # Fill in the data and create initialize form
        form = forms.RemoveAuthorizationForm(data=self.data)
        user = User.objects.get(email="user1@aalto.fi")
        form.instance = user

        try:
            with open(data_folder + '/delete_tokens', 'r') as token_file:
                num_lines_at_start = len(token_file.readlines())
        except:
            num_lines_at_start = 0

        # Set user as authorized
        user.authorized = True
        user.save()

        # Check that the form is valid and save
        self.assertTrue(form.is_valid())
        form.save()

        # Check that the authorization is revoked
        self.assertFalse(user.authorized)

        # Check that the user id has been added
        with open(data_folder + '/delete_tokens', 'r') as token_file:
            lines = token_file.readlines()
            assert(len(lines) == num_lines_at_start+1)
            correct_line = f'{self.user1.user_id}\n'
            self.assertEqual(lines[-1], correct_line)
