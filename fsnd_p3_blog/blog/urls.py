from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='main'),
    url(r'^user/$', views.test),
    url(r'^user/([A-Za-z0-9]+)/$', views.test),
    url(r'^newpost/$', views.test),
    url(r'^([0-9]+)/$', views.test),
    url(r'^([0-9]+)/edit/$', views.test),
    url(r'^([0-9]+)/delete/$', views.test),
    url(r'^([0-9]+)/like/$', views.test),
    url(r'^([0-9]+)/unlike/$', views.test),
    url(r'^([0-9]+)/([0-9]+)/edit/$', views.test),
    url(r'^([0-9]+)/([0-9]+)/delete/$', views.test),
    url(r'^([0-9]+)/([0-9]+)/like/$', views.test),
    url(r'^([0-9]+)/([0-9]+)/unlike/$', views.test),
    url(r'^signup/$', views.test),
    url(r'^welcome/$', views.test),
    url(r'^login/$', views.test),
    url(r'^logout/$', views.test)
]
