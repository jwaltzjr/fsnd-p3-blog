from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView

from . import models

# Create your views here.

class MainView(ListView):
    template_name = 'blog.html'
    model = models.BlogPost

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        # context['user'] = self.check_login()
        return context
