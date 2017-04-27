from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MainPage.as_view(), name='main'),
    url(r'^user/$', views.test, name='user_redirect'),
    url(r'^user/([A-Za-z0-9]+)/$', views.test, name='user_view'),
    url(r'^newpost/$', views.test, name='newpost'),
    url(r'^([0-9]+)/$', views.test, name='post_view'),
    url(r'^([0-9]+)/edit/$', views.test, name='post_edit'),
    url(r'^([0-9]+)/delete/$', views.test, name='post_delete'),
    url(r'^([0-9]+)/like/$', views.test, name='post_like'),
    url(r'^([0-9]+)/unlike/$', views.test, name='post_unlike'),
    url(r'^([0-9]+)/([0-9]+)/edit/$', views.test, name='comment_edit'),
    url(r'^([0-9]+)/([0-9]+)/delete/$', views.test, name='comment_delete'),
    url(r'^([0-9]+)/([0-9]+)/like/$', views.test, name='comment_like'),
    url(r'^([0-9]+)/([0-9]+)/unlike/$', views.test, name='comment_unlike'),
    url(r'^signup/$', views.test, name='signup'),
    url(r'^welcome/$', views.test, name='welcome'),
    url(r'^login/$', views.LoginPage.as_view(), name='login'),
    url(r'^logout/$', views.LogoutPage.as_view(), name='logout')
]
