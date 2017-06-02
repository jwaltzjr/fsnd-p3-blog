from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from . import models

# Create your views here.

class BlogPostView(DetailView):
    model = models.BlogPost
    context_object_name = 'post'

class BlogPostCreate(LoginRequiredMixin, CreateView):
    model = models.BlogPost
    fields = ['title', 'body']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BlogPostUpdate(LoginRequiredMixin, UpdateView):
    model = models.BlogPost
    fields = ['title', 'body']

    def get_object(self, queryset=None):
        blogpost = super().get_object()
        # Users can only update their own blogpost
        if blogpost.user != self.request.user:
            raise PermissionDenied
        return blogpost

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BlogPostDelete(LoginRequiredMixin, DeleteView):
    model = models.BlogPost
    success_url = reverse_lazy('main')

    def get_object(self, queryset=None):
        blogpost = super().get_object()
        # Users can only delete their own blogpost
        if blogpost.user != self.request.user:
            raise PermissionDenied
        return blogpost

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def main(request):
    posts = models.BlogPost.objects.all().order_by('-created')
    return render(request, 'blog/blog.html', {'posts': posts})

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

@login_required
def unlike_post(request, pk=None):
    post = get_object_or_404(models.BlogPost, pk=pk)
    try:
        like = models.Like.objects.filter(
            user = request.user,
            content_type = ContentType.objects.get_for_model(post.__class__),
            object_id = post.id
        ).get()
        like.delete()
    except models.Like.DoesNotExist:
        pass
    return redirect('post_view', pk=post.pk)

@login_required
def user_self_redirect(request):
    return redirect('user_view', username=request.user.username)

def user_list(request, username=None):
    user = get_object_or_404(User, username=username)
    posts = models.BlogPost.objects.filter(user=user).order_by('-created')
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
            return redirect('welcome')
    else:
        form = UserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})

@login_required
def welcome(request):
    return render(request, 'blog/welcome.html')
