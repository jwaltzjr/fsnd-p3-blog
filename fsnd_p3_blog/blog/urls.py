from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='main'),
]