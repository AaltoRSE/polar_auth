from django.shortcuts import render
from django.views.generic import DetailView
from users.models import User
from django.contrib.auth.decorators import login_required


@login_required
class UserDetailView(DetailView):
    model = User
