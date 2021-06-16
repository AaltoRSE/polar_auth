from django.dispatch import receiver
from survey.signals import survey_completed
from users.emails import send_enrolment_email


@receiver(survey_completed)
def check_enrolment(**kwargs):
    user = kwargs['user']
    if user.ready_to_authorize():
        send_enrolment_email(user.email)
