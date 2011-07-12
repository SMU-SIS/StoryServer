from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import quota
from google.appengine.api import memcache

import logging
import datetime
import urllib
import random
import base64

#from aeoid import users
from google.appengine.api import users
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from google.appengine.api.labs import taskqueue

#from django.utils.hashcompat import md5_constructor
from django.utils.html import escape
from operator import itemgetter

class User(db.Model):
    user_id = db.StringProperty(required=True)
    nickname = db.StringProperty(required=False)
    email = db.StringProperty(required=False)
    pic_url = db.StringProperty(required=False)

    @staticmethod
    def get_user(request):
        user = None
        session_id = None
        if hasattr(request, 'COOKIES'):
            if 'session_id' in request.COOKIES:
                session_id = request.COOKIES['session_id']
        else:
            if 'session_id' in request.cookies: #request.COOKIES:
                session_id = request.cookies['session_id']
                
        if session_id:
            session_id = base64.b64decode(session_id)
            logging.info('got session_id in cookies: ' + str(session_id))
            session = Session.get_session(session_id)
            if session:
                user = User.get_current_user(session.user_id)
        if not user:
            logging.warning('User not logged in')
        return user
    
    @staticmethod
    def get_current_user(user_id, nickname=None, email=None):
        if not user_id:
            return None
        user = User.all().filter('user_id =', user_id).get()
        if not user:
            user = User(user_id = user_id, nickname = nickname, email = email)
            user.put()
        return user

    @staticmethod
    def login(user_id, nickname=None, email=None):
        user = User.get_current_user(user_id, nickname, email)
        if not user:
            raise Exception('Login unsuccessful')
        return user
    
    @staticmethod
    def is_current_user_admin():
        return False
    
    @staticmethod
    def create_logout_url(target):
        return '/logout?target=' + str(target)
    
    @staticmethod
    def create_login_url(target):
        return '/login?target=' + str(target)

# Used to track logged in users    
class Session(db.Model):
    user_id = db.StringProperty(required=True)
    valid_until = db.DateTimeProperty(required=True)

    @staticmethod
    def create_session_for_user(user_id):
        Session.delete_session_for_user(user_id)
        valid_until = datetime.datetime.now() + datetime.timedelta(seconds = 86400)
        s = Session(user_id = user_id, valid_until = valid_until)
        s.put()
        return s.key().id()

    @staticmethod
    def delete_session_for_user(user_id):
        db.delete(Session.all().filter('user_id =', user_id))

    @staticmethod
    def get_session(session_id):
        try:
            s = Session.get_by_id(long(session_id))
            if s and s.valid_until > datetime.datetime.now():
                return s
        except Exception, e:
            logging.error('Error while getting session: '+str(e))
        return None

#The story that an author builds
class Story(db.Model):
	name = db.StringProperty(required=True)
	owner = db.ReferenceProperty(User, collection_name='stories', required=True)
	created = db.DateTimeProperty(auto_now_add=True)

# Stories consist of an ordered collection of StorySteps
class StoryStep(db.Model):
	name = db.StringProperty(required=True)
	story =  db.ReferenceProperty(Story, collection_name='storysteps', required=True)
	order = db.IntegerProperty(default=1)

# Tasks are urls that meet some constraints that users must develop. 
class Task(db.Model):
	name = db.StringProperty(required=True)
	storystep =  db.ReferenceProperty(StoryStep, collection_name='challenges', required=True)
	order = db.IntegerProperty(default=1)
	urlContains = db.StringProperty(default='appspot')
	urlContentContains = db.StringProperty(default='Hello')

# Videos in StorySteps and appear in some order. 
# Videos can be locked until all the Tasks of lower order (0,1,2) are accomplished.  
class Video(db.Model):
	name = db.StringProperty(required=True)
	storystep =  db.ReferenceProperty(StoryStep, collection_name='videos', required=True)
	url = db.StringProperty(default='http://www.youtube.com/watch?v=pRpeEdMmmQ0')
	order = db.IntegerProperty(default=1)
	
# A game is used to keep track of a user's progress in a game. 
# Users can save and restart their games
class Game(db.Model):
	name = db.StringProperty(required=True)
	story =  db.ReferenceProperty(Story, collection_name='games', required=True)
	owner = db.ReferenceProperty(User, collection_name='games', required=True)

# TaskUnlocks are used to keep track if a user has unlocked a task in a specific game. 
class TaskUnlock(db.Model):
	game =  db.ReferenceProperty(Game, collection_name='taskunlocks', required=True)
	task =  db.ReferenceProperty(Task, collection_name='taskunlocks', required=True)


