from google.appengine.ext import db

class User(db.Model):

    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()

class BlogPost(db.Model):

    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)

    def count_comments(self):
        return Comment.all().ancestor(self).count()

    def count_likes(self):
        return db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND direct_parent = :direct_parent',
            level = 'Post',
            direct_parent = self.key().id()
        ).count()

    def user_liked(self, user):
        return db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND user = :user AND direct_parent = :direct_parent',
            level = 'Post',
            user = user,
            direct_parent = self.key().id()
        ).get()

class Comment(db.Model):

    comment = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)

    def count_likes(self):
        return db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND direct_parent = :direct_parent',
            level = 'Comment',
            direct_parent = self.key().id()
        ).count()

    def user_liked(self, user):
        return db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND user = :user AND direct_parent = :direct_parent',
            level = 'Comment',
            user = user,
            direct_parent = self.key().id()
        ).get()

class Like(db.Model):

    user = db.ReferenceProperty(User, required = True)
    level = db.StringProperty(required = True)
    direct_parent = db.IntegerProperty(required = True)