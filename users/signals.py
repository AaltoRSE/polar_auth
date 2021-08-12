from django.dispatch import receiver
from survey.signals import survey_completed
from users.emails import send_enrolment_email
from survey.models.response import Response


@receiver(survey_completed)
def check_enrolment(**kwargs):
    user = kwargs['user']

    user.first_survey_done = True
    user.save()

    # Check survey responses and mark surveys filled by this user
    for response in Response.objects.all():
        if user.user_id == response.user_id:
            user.filled_surveys.add(response.survey)

    # if user.ready_to_authorize():
    #     send_enrolment_email(user.email)
