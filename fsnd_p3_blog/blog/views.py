from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth import views as auth_views

from . import models

# Create your views here.

def main(request):
    posts = models.BlogPost.objects.all().order_by('-created')
    return render(request, 'blog.html', context={'posts': posts})

class LoginPage(auth_views.LoginView):
    template_name = 'login.html'

class LogoutPage(auth_views.LogoutView):
    template_name = 'logout.html'

def test(request):
    return HttpResponse('testing, testing...')
