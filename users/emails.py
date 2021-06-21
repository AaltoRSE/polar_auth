from django.core.mail import send_mail

from polar_auth.settings import DEFAULT_FROM_EMAIL as from_address


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
    subject = "cor:ona study: You have registered successfully"
    message = '''Hi,

You are now enrolled to the cor:ona study! Soon, a fitness tracker will be mailed to you to the address you provided (if you have requested to receive one). If you do not receive it within 10 days, please contact us (talayeh.aledavood@aalto.fi).

Once you have the fitness tracker:

Recharge the fitness tracker and go to the study website and login. Follow the steps to create a Polar account and link it the cor:ona study (instructions will be provided).  At this stage most of what you will do is the same as what you have to do once you purchase a fitness tracker yourself. The extra steps related to this study are minimal.

After you link your fitness tracker to the study:

You will receive one short survey from us each month by email. These surveys will be short so they can be done in less than 5 minutes. Please try to answer them as soon as possible when you get the link. This would be very helpful for the research.

Thank you once again for your participation! If you have questions please check our Frequently Asked Questions or contact us: talayeh.aledavood@aalto.fi

Have a great summer,
The cor:ona study team
    '''

    html_message ='''Hi,

You are now enrolled to the cor:ona study! Soon, a fitness tracker will be mailed to you to the address you provided (if you have requested to receive one). If you do not receive it within 10 days, please contact us (talayeh.aledavood@aalto.fi).

<b>Once you have the fitness tracker:</b>

Recharge the fitness tracker and go to the study website and login. Follow the steps to create a Polar account and link it the cor:ona study (instructions will be provided).  At this stage most of what you will do is the same as what you have to do once you purchase a fitness tracker yourself. The extra steps related to this study are minimal.

<b>After you link your fitness tracker to the study:</b>

You will receive one short survey from us each month by email. These surveys will be short so they can be done in less than 5 minutes. Please try to answer them as soon as possible when you get the link. This would be very helpful for the research.

Thank you once again for your participation! If you have questions please check our Frequently Asked Questions or contact us: talayeh.aledavood@aalto.fi

Have a great summer,
The cor:ona study team
    '''

    send_mail(
        subject, message, from_address,
        [address],
        html_message = html_message,
        fail_silently=False,
    )