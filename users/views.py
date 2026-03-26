from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from dotenv import load_dotenv

from users.models import User

from .forms import UserRegisterForm

load_dotenv(override=True)


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        send_mail(
            'Добро пожаловать в магазин!',
            f'Спасибо за регистрацию, {user.email}!',
            'fedorskarvinko@yandex.ru',
            [user.email],
            fail_silently=False,
        )
        login(self.request, user)
        return redirect(self.success_url)
