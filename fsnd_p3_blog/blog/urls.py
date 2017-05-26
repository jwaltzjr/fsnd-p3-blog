from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

comment_patterns = [
    # url(r'^edit/$', views.test, name='comment_edit'),
    # url(r'^delete/$', views.test, name='comment_delete'),
    # url(r'^like/$', views.test, name='comment_like'),
    # url(r'^unlike/$', views.test, name='comment_unlike')
]

post_patterns = [
    url(r'^$', views.BlogPostView.as_view(), name='post_view'),
    url(r'^edit/$', views.BlogPostUpdate.as_view(), name='post_edit'),
    url(r'^delete/$', views.BlogPostDelete.as_view(), name='post_delete'),
    url(r'^like/$', views.like_post, name='post_like'),
    url(r'^unlike/$', views.unlike_post, name='post_unlike'),
    url(r'^(?P<comment_pk>[0-9]+)/', include(comment_patterns))
]

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^(?P<pk>[0-9]+)/', include(post_patterns)),
    url(r'^user/$', views.user_self_redirect, name='user_redirect'),
    url(r'^user/(?P<username>[A-Za-z0-9]+)/$', views.user_list, name='user_view'),
    url(r'^newpost/$', views.BlogPostCreate.as_view(), name='newpost'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^welcome/$', views.welcome, name='welcome'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout')
]
