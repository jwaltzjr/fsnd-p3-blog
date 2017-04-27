from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth import views as auth_views

from . import models

# Create your views here.

class MainPage(ListView):
    template_name = 'blog.html'
    model = models.BlogPost

class LoginPage(auth_views.LoginView):
    template_name = 'login.html'

class LogoutPage(auth_views.LogoutView):
    template_name = 'logout.html'

def test(request):
    return HttpResponse('testing, testing...')
