from django.core.mail import send_mail

from polar_auth.settings import DEFAULT_FROM_EMAIL as from_address


def send_enrolment_email(address):
    subject = "cor:ona study- Next steps"
    message = '''Hi,

Thank you for participating in the cor:ona study! We have received your answers to the initial questionnaire. Soon, a fitness tracker will be mailed to you (if you have requested to receive one). If you do not receive it within 10 days, please contact us.

Once you have the fitness tracker:

Recharge the fitness tracker and go to the study website and log in. Follow the steps to create a Polar account and link it to the cor:ona study (instructions will be provided).  At this stage most of what you will do is the same as what you have to do once you purchase a fitness tracker yourself. The extra steps related to this study are minimal.

Your enrollment is not complete until you link your fitness tracker to the cor:ona study.

Thank you once again for your participation! If you have questions please check our Frequently Asked Questions (https://corona.cs.aalto.fi/faq/) or contact us: talayeh.aledavood@aalto.fi

The cor:ona study team
'''
    html_message = '''<p>Hi,</p>

<p>
Thank you for participating in the cor:ona study! We have received your answers to the initial questionnaire. Soon, a fitness tracker will be mailed to you (if you have requested to receive one). If you do not receive it within 10 days, please contact us.
</p>

<p>
<b>Once you have the fitness tracker:</b>
</p>

<p>
Recharge the fitness tracker and go to the study website and log in. Follow the steps to create a Polar account and link it to the cor:ona study (instructions will be provided).  At this stage most of what you will do is the same as what you have to do once you purchase a fitness tracker yourself. The extra steps related to this study are minimal.
</p>

<p>
Your enrollment is not complete until you link your fitness tracker to the cor:ona study.
</p>

<p>
Thank you once again for your participation! If you have questions please check our
<a href="https://corona.cs.aalto.fi/faq/">Frequently Asked Questions</a> or contact us: <a href="mailto:talayeh.aledavood@aalto.fi">talayeh.aledavood@aalto.fi</a>.
</p>

<p>
The cor:ona study team
</p>
'''

    send_mail(
        subject, message, from_address, [address],
        html_message=html_message,
        fail_silently=False,
    )


def send_enrolment_complete_email(address):
    subject = "cor:ona study- Successfully enrolled!"
    message = '''Hi,

Congratulations! You are now fully enrolled in the cor:ona study!

Future steps:

You will receive one short questionnaire from us each month by email. These surveys will be short so they can be done in less than 5 minutes. Please try to answer them as soon as possible when you get the link. This would be very helpful for the research.

Thank you once again for your participation! If you have questions please check our Frequently Asked Questions (https://corona.cs.aalto.fi/faq/) or contact us: talayeh.aledavood@aalto.fi

The cor:ona study team
'''
    html_message = '''<p>Hi,</p>

<p>
Congratulations! You are now fully enrolled in the cor:ona study!
</p>

<p>
<b>Future steps:</b>
</p>

<p>
You will receive one short questionnaire from us each month by email. These surveys will be short so they can be done in less than 5 minutes. Please try to answer them as soon as possible when you get the link. This would be very helpful for the research.
</p>

<p>
Thank you once again for your participation! If you have questions please check our
<a href="https://corona.cs.aalto.fi/faq/">Frequently Asked Questions</a> or contact us: <a href="mailto:talayeh.aledavood@aalto.fi">talayeh.aledavood@aalto.fi</a>.
</p>

<p>
The cor:ona study team
</p>
'''

    send_mail(
        subject, message, from_address, [address],
        html_message=html_message,
        fail_silently=False,
    )

