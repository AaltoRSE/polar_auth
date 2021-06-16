import uuid

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from users.models import User, Subscriber
from users.emails import send_enrolment_email, send_registration_email


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        ''' Validate Aalto email addresses. '''
        email = self.cleaned_data['email']
        if not email.endswith("@aalto.fi"):
            raise ValidationError(
                    "Please provide an Aalto email address."
                )
        return email

    def clean_address(self):
        address = self.cleaned_data['address']
        has_device = self.cleaned_data['has_own_device']
        if address == "" and not has_device:
            raise ValidationError(
                "Please provide an address for mailing the fitness tracker."
            )
        return address

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
        fields = ['email', 'has_own_device', 'address', 'user_id']
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
