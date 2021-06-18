from django.core.mail import send_mail

from_address = "do_not_reply@domain.com"


def send_enrolment_email(address):
    subject = "You have succesfully enrolled in the cor:ona study"
    message = '''Hi,

Thank you for participating in the cor:ona study. You have completed the steps required to enroll in the study and we will send you a fitness tracker if you requested for one.

If you have any questions, contact us at talayeh.aledavood@aalto.fi.
    '''
    send_mail(
        subject, message, from_address,
        [address], fail_silently=False,
    )


def send_registration_email(address):
    subject = "You have succesfully registered in the cor:ona study"
    message = '''Hi,

Thank you for registering to participate in the cor:ona study. If you did not already, please go through the steps listed at https://corona.cs.aalto.fi to fully enroll in the study. If you need a fitness tracker, we will send one to you once you have completed these steps.

If you have any questions, contact us at talayeh.aledavood@aalto.fi.
    '''
    send_mail(
        subject, message, from_address,
        [address], fail_silently=False,
    )