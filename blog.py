#
#
# TO-DO:
#
# - Change from pre's to p's
# - Style!
# - Create README
#
#

import hashlib
import hmac
import jinja2
import os
import random
import re
import string
import time
import webapp2
from google.appengine.ext import db

# Project DB Classes
import datastore

# Don't Look!
pass_key = 'HJWhOu2gbn4EVcmQf'

# Regex for form validation
re_user = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
re_pass = re.compile(r'^.{3,20}$')
re_email = re.compile(r'^[\S]+@[\S]+.[\S]+$')

# Jijna directory + startup
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader= jinja2.FileSystemLoader(template_dir),
    autoescape = True
)

class Handler(webapp2.RequestHandler):

    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def validate(self, string, regex):
        return regex.match(string)

    def make_salt(self):
        # Random 8 digit salt string of letters + numbers
        return ''.join(random.choice(string.letters + string.digits) for _ in range(8))

    def secure_password(self, user, pw, salt=None):
        if not salt:
            salt = self.make_salt()
        # Using HMAC with sha256, excrypt the key, salt, username, and password together.
        secure_pass = hmac.new(pass_key + salt, user + pw, hashlib.sha256).hexdigest()
        return '%s|%s' % (secure_pass, salt) # Store the salt for validation

    def validate_login_username(self, user):
        if self.validate(user, re_user): # Regex check
            # Check if in DB
            return db.GqlQuery('SELECT * FROM User WHERE username = :user', user=user).get()
        else:
            return None

    def validate_login_password(self, user, pw):
        salt = str(user.password.split('|')[-1])
        # Grab the salt and re-encrypt
        secure_pass = hmac.new(pass_key + salt, user.username + pw, hashlib.sha256).hexdigest()
        if user.password == '%s|%s' % (secure_pass, salt): # Check if matches DB
            return user.key().id() # Returns user_id
        else:
            return None

    def secure_cookie(self, name, value):
        # Store with encrypted form for verification, using pass_key to avoid dictionary attacks
        value_hash = hmac.new(pass_key, str(value), hashlib.sha256).hexdigest()
        return '%s=%s|%s' % (name, value, value_hash)

    def validate_cookie(self, name, cookie):
        value = cookie.split('|')[0]
        # Encrypt the first part of the cookie and match with second
        if self.secure_cookie(name, value) == ('%s=%s' % (name,cookie)):
            return value
        else:
            return None

    def add_user(self, username, password, email=''):
        password_hash = self.secure_password(username, password) # Encrypt password
        user = datastore.User(username=username, password=password_hash, email=email) # Create a User
        key = user.put() # Insert into DB
        return key.id() # Return user_id

    def check_login(self, force_login=False):
        # Run on startup for almost every page
        # If (force_login == True), redirect to login if no user found
        cookie = self.request.cookies.get('user_id')
        if cookie:
            user_id = self.validate_cookie('user_id', cookie)
            if user_id:
                return datastore.User.get_by_id(int(user_id)) # If valid user, return the User object to the handler
            else:
                if force_login:
                    self.redirect('/login')
                else:
                    return None
        else:
            if force_login:
                self.redirect('/login')
            else:
                return None

    def login(self, user_id):
        cookie = self.secure_cookie('user_id', int(user_id)) + '; path=/' # Create login cookie
        self.response.headers.add_header('Set-Cookie',cookie) # Set login cookie
        self.redirect('/welcome')


class MainPage(Handler):

    def get(self):
        # Front page, post all posts
        user = self.check_login()
        posts = datastore.BlogPost.all().order('-created')
        self.render(
            'blog.html',
            posts = posts,
            user = user
        )

class UserPage(Handler):

    def get(self, username=None):
        # Post all posts by a given user.
        user = self.check_login()
        if user and not username:
            # If no username is given and you're logged in, show your posts
            page_user = user
        else:
            # Otherwise get the user
            page_user = db.GqlQuery(
                'SELECT * FROM User WHERE username = :username',
                username = username
            ).get()

        if page_user:
            posts = db.GqlQuery(
                'SELECT * FROM BlogPost WHERE user = :user ORDER BY created',
                user = page_user
            ).fetch(100)
            self.render(
                'blog.html',
                posts = posts,
                user = user
            )
        else:
            self.redirect('/')

class EntryPage(Handler):

    def render_page(self, user, title='', body='', error=''):
        self.render(
            'newpost.html',
            title = title,
            body = body,
            error = error,
            user = user
        )

    def get(self):
        user = self.check_login(force_login=True)
        self.render_page(user)

    def post(self):
        user = self.check_login(force_login=True)
        title = self.request.get('subject')
        body = self.request.get('content')

        if title and body:
            # Create a row and insert into database
            blogpost = datastore.BlogPost(title = title, body = body, user = user)
            key = blogpost.put()
            post_id = key.id() # ID for permalink
            self.redirect('/%s' % post_id)
        else:
            error = 'Title and content are required.'
            self.render_page(user, title, body, error)

class PostPage(Handler):

    def render_page(self, post, user, error_comment=''):

        if not post:
            self.error(404)
            return
        else:
            comments = datastore.Comment.all().ancestor(post).order('-created')
            self.render(
                'post.html',
                user = user,
                comments = comments,
                post = post,
                error_comment = error_comment
            )

    def get(self, post_id):
        user = self.check_login()
        post = datastore.BlogPost.get_by_id(int(post_id))
        self.render_page(post, user)

    def post(self, post_id):
        user = self.check_login(force_login=True)
        text = self.request.get('comment')

        if text:
            post = datastore.BlogPost.get_by_id(int(post_id))
            # Create a row and insert into database
            comment = datastore.Comment(parent=post, comment = text, user = user)
            comment.put()
            self.redirect('/%s' % post_id)
        else:
            self.render_page(post, user, error_comment = 'No comment found.')

class EditPostPage(Handler):

    def render_page(self, post, user, title='', body='', error=''):

        if not post:
            self.error(404)
            return
        else:
            # Display all comments with the current post as parent
            comments = datastore.Comment.all().ancestor(post).order('-created')
            self.render(
                'newpost.html',
                title = title,
                body = body,
                error = error,
                user = user
            )

    def get(self, post_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))

        if user.key().id() == post.user.key().id():
            self.render_page(post, user, post.title, post.body)
        else:
            self.redirect('/%s' % post.key().id())

    def post(self, post_id):
        user = self.check_login(force_login=True)
        post = datastore.BlogPost.get_by_id(int(post_id))
        title = self.request.get('subject')
        body = self.request.get('content')

        if title and body:
            post.title = title # Update the object
            post.body = body
            key = post.put()
            post_id = key.id() # ID for permalink
            self.redirect('/%s' % post_id)
        else:
            error = 'Title and content are required.'
            self.render_page(post, user, title, body, error)

class EditCommentPage(Handler):

    def render_page(self, post, user, comment='', error=''):

        if not post:
            self.error(404)
            return
        else:
            # Display all comments with the current post as parent
            comments = datastore.Comment.all().ancestor(post).order('-created')
            self.render(
                'editcomment.html',
                post = post,
                comment = comment,
                error = error,
                user = user
            )

    def get(self, post_id, comment_id):
        user = self.check_login(force_login = True)

        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)
        
        if user.key().id() == comment.user.key().id():
            self.render_page(post, user, comment.comment)
        else:
            self.redirect('/%s' % post.key().id())

    def post(self, post_id, comment_id):

        user = self.check_login(force_login=True)

        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)
        comment_text = self.request.get('content')

        if comment_text:
            comment.comment = comment_text # update the object
            comment.put()
            self.redirect('/%s' % post_id)
        else:
            error = 'A comment is required.'
            self.render_page(post, user, title, body, error)

class DeletePostPage(Handler):

    def render_page(self, post, user, error = ''):

        if not post:
            self.error(404)
            return
        else:
            self.render(
                'delete_post.html',
                post = post,
                user = user,
                error = error
            )

    def get(self, post_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))

        if user.key().id() == post.user.key().id():
            self.render_page(post, user)
        else:
            self.redirect('/%s' % post.key().id())


    def post(self, post_id):
        user = self.check_login(force_login=True)
        post = datastore.BlogPost.get_by_id(int(post_id))

        if user.key().id() == post.user.key().id():
            post.delete()
            time.sleep(.2) # Hack because of datastore issues
            self.redirect('/')
        else:
            self.redirect('/%s' % post.key().id())

class DeleteCommentPage(Handler):

    def render_page(self, post, comment, user):
        if not comment:
            self.error(404)
            return
        else:
            self.render(
                'delete_comment.html',
                post = post,
                comment = comment,
                user = user
            )

    def get(self, post_id, comment_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)

        if user.key().id() == comment.user.key().id():
            self.render_page(post, comment, user)
        else:
            self.redirect('/%s/%s' % ( post.key().id()), comment.key().id() )


    def post(self, post_id, comment_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)

        if user.key().id() == comment.user.key().id():
            comment.delete()
            time.sleep(.2) # Hack because of datastore issues
            self.redirect('/%s' % post_id)
        else:
            self.redirect('/%s/%s' % ( post.key().id()), comment.key().id() )

class LikePost(Handler):

    def get(self, post_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))

        if user.key().id() != post.user.key().id(): # Can't like your own post
            like = datastore.Like.get_or_insert( # No duplicates
                'P' + user.username + str(post.key().id()), # Unique key
                user = user,
                level = 'Post',
                direct_parent = post.key().id()
            )
            time.sleep(.2) # Hack because of datastore issues
        
        self.redirect('/%s' % post_id)

class LikeComment(Handler):

    def get(self, post_id, comment_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)

        if user.key().id() != comment.user.key().id(): # Can't like your own comment
            like = datastore.Like.get_or_insert( # No duplicates
                'C' + user.username + str(comment.key().id()), # Unique key
                user = user,
                level = 'Comment',
                direct_parent = comment.key().id()
            )
            time.sleep(.2) # Hack because of datastore issues

        self.redirect('/%s' % post_id)

class UnlikePost(Handler):

    def get(self, post_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))

        like = db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND user = :user AND direct_parent = :direct_parent',
            level = 'Post',
            user = user,
            direct_parent = post.key().id()
        ).get()
        if like:
            like.delete()
            time.sleep(.2) # Hack because of datastore issues

        self.redirect('/%s' % post_id)

class UnlikeComment(Handler):

    def get(self, post_id, comment_id):
        user = self.check_login(force_login = True)
        post = datastore.BlogPost.get_by_id(int(post_id))
        comment = datastore.Comment.get_by_id(int(comment_id), parent = post)

        like = db.GqlQuery(
            'SELECT * FROM Like WHERE level = :level AND user = :user AND direct_parent = :direct_parent',
            level = 'Comment',
            user = user,
            direct_parent = comment.key().id()
        ).get()
        if like:
            like.delete()
            time.sleep(.2) # Hack because of datastore issues

        self.redirect('/%s' % post_id)

class SignupPage(Handler):

    def get(self):
        user = self.check_login()
        if user:
            self.redirect('/')
        else:
            self.render('signup.html')

    def post(self):

        user = self.check_login()
        if user:
            self.redirect('/')
        else:

            in_user = self.request.get('username')
            if in_user and not self.validate(in_user, re_user): # Regex check
                er_user = 'That is not a valid username.'
            else:
                if not in_user: # Null check
                    er_user  = 'You must provide a valid username.'
                elif self.validate_login_username(in_user): # Duplicate user check
                    er_user = 'That username already exists.'
                else: # Success
                    er_user = ''

            in_pass = self.request.get('password')
            if in_pass and not self.validate(in_pass, re_pass): # Regex check
                er_pass = 'That is not a valid password.'
            else:
                if not in_pass: # Null check
                    er_pass  = 'You must provide a valid password.'
                else: # Success
                    er_pass = ''

            in_verify = self.request.get('verify')
            if in_verify and in_pass != in_verify: # Compare to password 1 in_pass
                er_verify = 'The passwords did not match.'
            else:
                if not in_verify: # Null check
                    er_verify  = 'The passwords did not match.'
                else: # Success 
                    er_verify = ''

            in_email = self.request.get('email')
            if in_email and not self.validate(in_email, re_email): # Regex check
                er_email = 'That is not a valid email.'
            else: # Success
                er_email = ''

            if er_user == er_pass == er_verify == er_email == '':
                user_id = self.add_user(in_user, in_pass, in_email) # Create a User
                self.login(user_id) # Create a user_id cookie to login
            else: # Re-render if errors
                self.render(
                    'signup.html',
                    error_username = er_user,
                    error_password = er_pass,
                    error_verify = er_verify,
                    error_email = er_email,
                    old_user = in_user,
                    old_email = in_email,
                    user = user
                )

class WelcomePage(Handler):

    def get(self):
        user = self.check_login(force_login=True)
        self.render('welcome.html', user = user)

class LoginPage(Handler):

    def render_page(self, error_username = '', error_password = '', old_user = ''):
        self.render(
            'login.html',
            error_username = error_username,
            error_password = error_password,
            old_user = old_user,
        )

    def get(self):
        if self.check_login():
            self.redirect('/')
        else:
            self.render_page()

    def post(self):

        user = self.check_login()
        if user:
            self.redirect('/')
        else:

            in_user = self.request.get('username')
            user = self.validate_login_username(in_user) # Regex check and User in DB Check
            if in_user and not user:
                er_user = 'Invalid username or password.'
            else:
                if not in_user:
                    er_user  = 'Invalid username or password.'
                else:
                    er_user = ''

            in_pass = self.request.get('password')
            if in_pass and not self.validate(in_pass, re_pass): # Regex check
                er_user = 'Invalid username or password.'
            else:
                if not in_pass:
                    er_pass  = 'Invalid username or password.'
                else:
                    er_pass = ''

            if er_user == er_pass == '':
                user_id = self.validate_login_password(user, in_pass) # Check user name and password
                if user_id:
                    self.login(user_id) # Set user_id cookie to login
                else:
                    self.render_page(
                        error_username = 'Invalid username or password.',
                        old_user = in_user
                    )
            else:
                self.render_page(
                    error_username = er_user,
                    error_password = er_pass,
                    old_user = in_user
                )

class LogoutPage(Handler):

    def get(self):
        # Set a blank header that expired in the past to delete the cookie
        self.response.headers.add_header('Set-Cookie','user_id=; path=/; expires=Thu, 3 Jan 1980 12:00:00 UTC')
        self.redirect('/login')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/user', UserPage),
    (r'/user/([A-Za-z0-9]+)', UserPage),
    ('/newpost', EntryPage),
    (r'/([0-9]+)', PostPage),
    (r'/([0-9]+)/edit', EditPostPage),
    (r'/([0-9]+)/delete', DeletePostPage),
    (r'/([0-9]+)/like', LikePost),
    (r'/([0-9]+)/unlike', UnlikePost),
    (r'/([0-9]+)/([0-9]+)/edit', EditCommentPage),
    (r'/([0-9]+)/([0-9]+)/delete', DeleteCommentPage),
    (r'/([0-9]+)/([0-9]+)/like', LikeComment),
    (r'/([0-9]+)/([0-9]+)/unlike', UnlikeComment),
    ('/signup', SignupPage),
    ('/welcome', WelcomePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage)
], debug=True)