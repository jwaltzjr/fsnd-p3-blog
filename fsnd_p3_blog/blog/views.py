from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.views.generic import TemplateView, ListView
from django.contrib.auth import login, authenticate, views as auth_views
from django.contrib.auth.forms import UserCreationForm

from . import models

# Create your views here.

def main(request):
    posts = models.BlogPost.objects.all().order_by('-created')
    context = RequestContext(request, {'post': posts})
    return render(request, 'blog.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('main')
    else:
        form = UserCreationForm()
    context = RequestContext(request, {'form': form})
    return render(request, 'signup.html', context)

class LoginPage(auth_views.LoginView):
    template_name = 'login.html'

class LogoutPage(auth_views.LogoutView):
    template_name = 'logout.html'

def test(request):
    return HttpResponse('testing, testing...')
