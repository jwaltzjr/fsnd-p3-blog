from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    # url(r'^user/$', views.test, name='user_redirect'),
    # url(r'^user/([A-Za-z0-9]+)/$', views.test, name='user_view'),
    url(r'^newpost/$', views.BlogPostCreate.as_view(), name='newpost'),
    url(r'^(?P<pk>[0-9]+)/$', views.test, name='post_view'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.BlogPostUpdate.as_view(), name='post_edit'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.BlogPostDelete.as_view(), name='post_delete'),
    # url(r'^(?P<pk>[0-9]+)/like/$', views.test, name='post_like'),
    # url(r'^(?P<pk>[0-9]+)/unlike/$', views.test, name='post_unlike'),
    # url(r'^([0-9]+)/([0-9]+)/edit/$', views.test, name='comment_edit'),
    # url(r'^([0-9]+)/([0-9]+)/delete/$', views.test, name='comment_delete'),
    # url(r'^([0-9]+)/([0-9]+)/like/$', views.test, name='comment_like'),
    # url(r'^([0-9]+)/([0-9]+)/unlike/$', views.test, name='comment_unlike'),
    url(r'^signup/$', views.signup, name='signup'),
    # url(r'^welcome/$', views.test, name='welcome'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout')
]
