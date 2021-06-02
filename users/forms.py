from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User, Subscriber


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']


class ConsentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['consent']


class SubscriptionForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Subscriber
        fields = ['email']