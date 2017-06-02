from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

# Create your models here.

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    content_type = models.ForeignKey(ContentType, blank=False)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

class BlogPost(models.Model):
    title = models.CharField(max_length=32, blank=False)
    body = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = GenericRelation(Like)
    published = models.BooleanField(default=False)
    publish_time = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('post_view', kwargs={'pk': self.pk})

    def publish(self):
        self.published = True
        self.published_time = timezone.now()
        self.save()
        return self

    def count_comments(self):
        return self.comment_set.all().count()

    def count_likes(self):
        return self.likes.all().count()

    def user_liked(self, user):
        if user.is_authenticated:
            try:
                user_like = self.likes.filter(user=user).get()
            except Like.DoesNotExist:
                user_like = None
        else:
            user_like = None
        return user_like

class Comment(models.Model):
    comment = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    post = models.ForeignKey('BlogPost', blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = GenericRelation(Like)

    def count_likes(self):
        return self.likes.all().count()

    def user_liked(self, user):
        if user.is_authenticated:
            try:
                user_like = self.likes.filter(user=user).get()
            except Like.DoesNotExist:
                user_like = None
        else:
            user_like = None
        return user_like
