import requests
import base64

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import authenticate, login
from django.core.mail import send_mass_mail
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

import users.forms
from users.data_server import communicate_token
from users.models import User, Subscriber
from users.emails import send_enrolment_complete_email
from polar_auth.settings import polar_key, polar_secret
from polar_auth.settings import DEFAULT_FROM_EMAIL as from_address


class UserView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class ConsentSuccessView(UserView):
    template_name = 'users/consent_success.html'


class FAQView(UserView):
    template_name = 'faq.html'


class AboutView(UserView):
    template_name = 'about.html'


class AboutInitialView(SuccessMessageMixin, CreateView):
    template_name = 'about_initial.html'
    success_url = reverse_lazy('about')
    form_class = users.forms.SubscriptionForm
    success_message = "Thank you for subscribing to updates."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class EmailSubscribersView(UserPassesTestMixin, FormView):
    template_name = 'users/subscriber_email.html'
    form_class = users.forms.EmailSubscribersForm
    success_url = reverse_lazy('main')

    def test_func(self):
        return self.request.user.is_superuser

    def send_email(self, data):
        subject = data['subject']
        message = data['message']

        subscribers = Subscriber.objects.all()

        emails = [(subject, message, from_address, [subscriber.email])
                  for subscriber in subscribers
                  ]
        send_mass_mail(emails, fail_silently=False)

    def form_valid(self, form):
        self.send_email(form.cleaned_data)
        return super().form_valid(form)


class RegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/registration.html'
    form_class = users.forms.UserRegisterForm
    success_message = "Your profile was created successfully"

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user = authenticate(username=email, password=password)
        login(self.request, user)
        return HttpResponseRedirect(reverse_lazy('privacy'))


@method_decorator(login_required, name='dispatch')
class PrivacyView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/privacy_notice.html'
    success_url = reverse_lazy('consent')
    form_class = users.forms.PrivacyForm
    success_message = "Your reply has been registered succesfully."

    def get_success_url(self):
        user = self.request.user
        if not user.consent:
            return '/consent/'
        if not user.first_survey_done:
           return '/surveys/1'
        return '/'

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class ConsentView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/consent.html'
    success_url = '/surveys/1'
    form_class = users.forms.ConsentForm
    success_message = "Your consent has been registered succesfully"

    def get_success_url(self):
        user = self.request.user
        if not user.privacy:
           return '/privacy/'
        if not user.first_survey_done:
           return '/surveys/1'
        return '/'

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class AddAuthTokenView(RedirectView):

    def get_access_token(self, token):
        ''' We ask for an access token using the received OAuth2 token
            (this is where we authenticate ourselves)
        '''
        auth = f'{polar_key}:{polar_secret}'
        auth_bytes = auth.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')

        headers = {
          'Authorization': f'Basic {base64_auth}'
        }
        data = f"grant_type=authorization_code&code={token}"

        url = 'https://polarremote.com/v2/oauth2/token/'
        if not settings.TESTING:
            response = requests.post(
                url,
                data=data,
                headers=headers
            ).json()
        else:
            # Fake a response in debug mode
            response = {
                "x_user_id": "debug_id",
                "access_token": "debug_token"
            }
        return response

    def register_user_token(self, username, access_token):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        json = {"member-id": username}

        # Note that there is no DEBUG equivalent of this, changes only on
        # Polar side
        if not settings.TESTING:
            requests.post(
                'https://www.polaraccesslink.com/v3/users',
                json=json,
                headers=headers
            )

    def get_redirect_url(self, *args, **kwargs):
        # The user get's redirected here with a token in the url
        user = self.request.user
        token = self.request.GET.get('code', '')
        token_response = self.get_access_token(token)

        # Extract the Polar ID and the access token
        user.polar_id = token_response["x_user_id"]
        access_token = token_response["access_token"]

        # Mark user as authorized
        user.authorized = True

        # Send the user information to the data server
        communicate_token(user.polar_id, access_token, user.user_id)
        user.save()

        # Email the user
        send_enrolment_complete_email(user.email)

        # Register the user
        self.register_user_token(user.username, access_token)

        return reverse_lazy('about')


@method_decorator(login_required, name='dispatch')
class GetAuthenticationView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        url = "https://flow.polar.com/oauth2/authorization"
        url += "?response_type=code"
        url += "&scope=accesslink.read_all"
        url += f"&client_id={polar_key}"
        return url


@method_decorator(login_required, name='dispatch')
class Remove_authorization(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/remove_authorization.html'
    success_url = '/'
    form_class = users.forms.RemoveAuthorizationForm
    success_message = "Authorization removed"

    def get_object(self):
        return self.request.user

