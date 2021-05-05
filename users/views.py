from django.shortcuts import render
from django.views.generic import DetailView
from users.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404


@method_decorator(login_required, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = "userdetailview.html"

    def get_object(self):
        object = self.kwargs.get('username')
        print(self.request.user)
        return self.request.user
