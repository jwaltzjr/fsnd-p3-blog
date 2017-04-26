from django.db import models
from django.contrib import contenttypes

# Create your models here.

class User(models.Model):
    username = models.CharField(required=True)
    password = models.CharField(required=True)
    email = models.EmailField()

class BlogPost(models.Model):
    title = models.CharField(required=True)
    body = models.TextField(required=True)
    user = models.ForeignKey('User', required=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = contenttypes.fields.GenericRelation(
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
    comment = models.TextField(required=True)
    user = models.ForeignKey('User', required=True)
    post = models.ForeignKey('BlogPost', required=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    likes = contenttypes.fields.GenericRelation(
        Like,
        content_type_field='level',
        object_id_field='parent_id',
    )

    def count_likes(self):
        return self.likes.all().count()

    def user_liked(self, user):
        return self.likes.filter(user=user).get()

class Like(models.Model):
    user = models.ForeignKey('User', required=True)
    level = models.ForeignKey(contenttypes.models.ContentType, required=True)
    parent_id = models.PositiveIntegerField()
    direct_parent = contenttypes.fields.GenericForeignKey('level', 'parent_id')
