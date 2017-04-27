from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=32, blank=False)
    password = models.CharField(max_length=32, blank=False)
    email = models.EmailField()

class Like(models.Model):
    user = models.ForeignKey('User', blank=False)
    level = models.ForeignKey(ContentType, blank=False)
    parent_id = models.PositiveIntegerField()
    direct_parent = GenericForeignKey('level', 'parent_id')

class BlogPost(models.Model):
    title = models.CharField(max_length=32, blank=False)
    body = models.TextField(blank=False)
    user = models.ForeignKey('User', blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = GenericRelation(
        Like,
        content_type_field='level',
        object_id_field='parent_id',
    )

    def count_comments(self):
        return self.comment_set.all().count()

    def count_likes(self):
        return self.likes.all().count()

    def user_liked(self, user):
        return self.likes.filter(user=user).get()

class Comment(models.Model):
    comment = models.TextField(blank=False)
    user = models.ForeignKey('User', blank=False)
    post = models.ForeignKey('BlogPost', blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = GenericRelation(
        Like,
        content_type_field='level',
        object_id_field='parent_id',
    )

    def count_likes(self):
        return self.likes.all().count()

    def user_liked(self, user):
        return self.likes.filter(user=user).get()
