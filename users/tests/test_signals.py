from .user_test_case import UserTestCase
from survey.signals import survey_completed
from survey.models import Survey, Response


class SignalTestCase(UserTestCase):
    def setUp(self):
        super().setUp()

    def test_survey_completed(self):
        ''' Check the survey_completed signal '''

        # log in user1
        self.client.login(
            username=self.user1_data['email'],
            password=self.user1_data['password']
        )

        # Mock a response, since we dont use it
        survey = Survey()
        survey.need_logged_user = True
        survey.save()
        response = Response()
        response.survey = survey
        response.user_id = self.user1.user_id
        response.save()
        data = {}

        # send the signal
        survey_completed.send(
            sender=Response,
            instance=response,
            data=data,
            user=self.user1
        )

        # Check that the survey got recorded to the user
        self.assertEqual(self.user1.filled_surveys.get(pk=survey.pk), survey)


