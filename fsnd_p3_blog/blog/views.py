from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login, authenticate, views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy


from . import models

# Create your views here.

def main(request):
    posts = models.BlogPost.objects.all().order_by('-created')
    return render(request, 'blog/blog.html', {'posts': posts})

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
    return render(request, 'blog/signup.html', {'form': form})

class BlogPostView(DetailView):
    model = models.BlogPost
    context_object_name = 'post'

class BlogPostCreate(LoginRequiredMixin, CreateView):
    model = models.BlogPost
    fields = ['title', 'body']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BlogPostCreate, self).form_valid(form)

class BlogPostUpdate(LoginRequiredMixin, UpdateView):
    model = models.BlogPost
    fields = ['title', 'body']

    def get_object(self, queryset=None):
        blogpost = super(BlogPostUpdate, self).get_object()
        if blogpost.user != self.request.user:
            raise PermissionDenied
        return blogpost

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BlogPostUpdate, self).form_valid(form)

class BlogPostDelete(LoginRequiredMixin, DeleteView):
    model = models.BlogPost
    success_url = reverse_lazy('main')

    def get_object(self, queryset=None):
        blogpost = super(BlogPostDelete, self).get_object()
        if blogpost.user != self.request.user:
            raise PermissionDenied
        return blogpost

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BlogPostDelete, self).form_valid(form)

@login_required
def like_post(request, pk=None):
    post = get_object_or_404(models.BlogPost, pk=pk)
    if request.user != post.user: # Can't like your own post
        like = models.Like.objects.get_or_create(
            user = request.user,
            content_type = ContentType.objects.get_for_model(post.__class__),
            object_id = post.id
        )
    return redirect('post_view', pk=post.pk)


def test(request):
    return HttpResponse('testing, testing...')
