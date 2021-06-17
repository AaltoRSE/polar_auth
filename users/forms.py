import uuid
import base64
import paramiko

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from users.models import User, Subscriber
from users.emails import send_enrolment_email, send_registration_email
from polar_auth.settings import data_server, data_folder, data_server_key
from polar_auth.settings import rsa_key_file, ssh_username

# Set up an SSH client and add the data server key
server_key = paramiko.RSAKey(data=base64.decodebytes(data_server_key))
ssh_client = paramiko.SSHClient()
ssh_client.get_host_keys().add(data_server, 'ssh-rsa', server_key)
rsa_key = paramiko.RSAKey.from_private_key_file(rsa_key_file)


# Communicate the access token to the data server
def communicate_token(polar_id, access_token, subject_id):
    ''' Communicate a token to the data server over ssh. '''

    ssh_client.connect(hostname=data_server, username=ssh_username, pkey=rsa_key)
    sftp_client = ssh_client.open_sftp()
    remote_file = data_folder + '/new_tokens'
    token_file = sftp_client.file(remote_file, mode='a', bufsize=1)
    token_file.write(f'{access_token} {polar_id} {subject_id}\n')
    token_file.flush()
    token_file.close()


# Communicate the access token to the data server
def delete_token(subject_id):
    ''' Communicate a token to the data server over ssh. '''

    ssh_client.connect(hostname=data_server, username=ssh_username, pkey=rsa_key)
    sftp_client = ssh_client.open_sftp()
    remote_file = data_folder + '/delete_tokens'
    token_file = sftp_client.file(remote_file, mode='a', bufsize=1)
    token_file.write(f'{subject_id}\n')
    token_file.flush()
    token_file.close()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    has_own_device = forms.BooleanField(required=False, widget=widget,
            label=User._meta.get_field('has_own_device').verbose_name,
            help_text=User._meta.get_field('has_own_device').help_text,
        )
    full_time = forms.BooleanField(required=True, widget=widget,
            label='I am currently a full-time Aalto employee',
            help_text=mark_safe('<ul><li>"visitor" status is not eligible</li></ul>'),
        )
    do_not_foresee_changing_employer = forms.BooleanField(
            required=True, widget=widget,
            label=mark_safe('I do not expect to change my employer during the next 6 months (this is <i>not</i> a commitment)')
        )
    will_return_tracker = forms.BooleanField(required=True, widget=widget,
            label='If I receive a fitness tracker, I will return it to Aalto University once the study is over or at any point if I decide to drop out of the study or if I change employer'
        )

    def clean_email(self):
        ''' Validate Aalto email addresses. '''
        email = self.cleaned_data['email']
        if not email.endswith("@aalto.fi"):
            raise ValidationError(
                    "Please provide an Aalto email address."
                )
        return email

    def clean_home_address(self):
        home_address = self.cleaned_data['home_address']
        has_device = self.cleaned_data['has_own_device']
        if home_address == "" and not has_device:
            raise ValidationError(
                "Please provide an address for mailing the fitness tracker."
            )
        return home_address

    def clean(self):
        ''' Create a random user_id '''
        cleaned_data = super().clean()
        cleaned_data['user_id'] = int(uuid.uuid1().int>>96)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit)
        send_registration_email(user.email)
        return user

    class Meta:
        model = User
        fields = ['email', 'has_own_device', 'home_address', 'user_id']
        widgets = {'user_id': forms.HiddenInput()}


class PrivacyForm(forms.ModelForm):
    widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    privacy = forms.BooleanField(required=True, widget=widget)

    def save(self, commit=True):
        user = super().save(commit)
        if user.ready_to_authorize():
            send_enrolment_email(user.email)
        return user

    class Meta:
        model = User
        fields = ['privacy']


class ConsentForm(forms.ModelForm):

    # Consent consists of multiple questions. Add each here.
    widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    field_1 = forms.BooleanField(required=True, widget=widget)
    field_2 = forms.BooleanField(required=True, widget=widget)
    field_3 = forms.BooleanField(required=True, widget=widget)
    field_4 = forms.BooleanField(required=True, widget=widget)
    field_5 = forms.BooleanField(required=True, widget=widget)
    field_6 = forms.BooleanField(required=True, widget=widget)

    class Meta:
        model = User
        fields = ['consent']

    def save(self, commit=True):
        user = super().save(commit)
        if user.ready_to_authorize():
            send_enrolment_email(user.email)
        return user

    def clean(self):
        ''' If the form gets submitted, the user has consented to all the
            items. We can just set consent to true. '''
        cleaned_data = super().clean()
        cleaned_data['consent'] = True
        return cleaned_data


class RemoveAuthorizationForm(forms.ModelForm):

    # Consent consists of multiple questions. Add each here.
    widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    Remove_authorization = forms.BooleanField(required=True, widget=widget)

    class Meta:
        model = User
        fields = ['Remove_authorization']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.authorized = False
        user = super().save(commit)
        delete_token(user.user_id)
        return user


class SubscriptionForm(forms.ModelForm):
    email = forms.EmailField()

    def clean_email(self):
        ''' Validate Aalto email addresses. '''
        email = self.cleaned_data['email']
        if not email.endswith("@aalto.fi"):
            raise ValidationError(
                    "Please provide an Aalto email address."
                )
        return email

    class Meta:
        model = Subscriber
        fields = ['email']
