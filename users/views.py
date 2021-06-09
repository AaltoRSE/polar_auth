import requests
import base64
import uuid
import paramiko

from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

import users.forms
from users.models import User
from polar_auth.settings import polar_key, polar_secret
from polar_auth.settings import data_server, data_folder, data_server_key

# Set up an SSH client and add the data server key
server_key = paramiko.RSAKey(data=base64.decodebytes(data_server_key))
ssh_client = paramiko.SSHClient()
ssh_client.get_host_keys().add(data_server, 'ssh-rsa', server_key)


# Communicate the access token to the data server
def communicate_token(polar_id, access_token, subject_id):
    ''' Communicate a token to the data server over ssh. '''

    ssh_client.connect(hostname=data_server)
    sftp_client = ssh_client.open_sftp()
    remote_file = data_folder + '/new_tokens'
    token_file = sftp_client.file(remote_file, mode='a', bufsize=1)
    token_file.write(f'{access_token} {polar_id} {subject_id}\n')
    token_file.flush()
    token_file.close()


class FAQView(TemplateView):
    template_name = 'faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class TestView(TemplateView):
    template_name = 'workflow_test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


class AboutView(SuccessMessageMixin, CreateView):
    template_name = 'about.html'
    success_url = reverse_lazy('about')
    form_class = users.forms.SubscriptionForm
    success_message = "Thank you for subscribing to updates."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = "users/detailview.html"

    def get_object(self):
        return self.request.user


class RegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')
    form_class = users.forms.UserRegisterForm
    success_message = "Your profile was created successfully"


class PrivacyView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/privacy_notice.html'
    success_url = reverse_lazy('consent')
    form_class = users.forms.PrivacyForm
    success_message = "Your reply has been registered succesfully."

    def get_object(self):
        return self.request.user


class ConsentView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/consent.html'
    success_url = reverse_lazy('about')
    form_class = users.forms.ConsentForm
    success_message = "Your consent has been registered succesfully"

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class AddAuthTokenView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        # The user get's redirected here with a token in the url
        user = self.request.user
        token = self.request.GET.get('code', '')

        # We ask for an access token using the received token
        # (this is where we authenticate ourselves)
        auth = f'{polar_key}:{polar_secret}'
        auth_bytes = auth.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')

        headers = {
          'Authorization': f'Basic {base64_auth}'
        }
        data = f"grant_type=authorization_code&code={token}"

        token_response = requests.post('https://polarremote.com/v2/oauth2/token/',
                          data=data,
                          headers=headers
                          ).json()

        user.polar_id = token_response["x_user_id"]
        access_token = token_response["access_token"]
        subject_id = uuid.uuid1().int>>64
        # Send the user information to the data server
        communicate_token(user.polar_id, access_token, subject_id)
        user.save()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token_response["access_token"]}'
        }
        json={"member-id": user.username}

        r = requests.post('https://www.polaraccesslink.com/v3/users', json=json, headers = headers)

        return reverse_lazy('home')


@method_decorator(login_required, name='dispatch')
class GetAuthenticationView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        url = "https://flow.polar.com/oauth2/authorization"
        url += "?response_type=code"
        url += "&scope=accesslink.read_all"
        url += f"&client_id={polar_key}"
        return url
