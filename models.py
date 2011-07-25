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

# Add Janrain look-up code from db if not there. 
# Add Google account users for spreadsheet support. 

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

class UserTag(db.Model):
  user = db.ReferenceProperty(User, required=True)
  tag = db.StringProperty(required=True)
  tagOrder = db.IntegerProperty(default=1,required=True)
  created = db.DateTimeProperty(auto_now_add=True)

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
    description = db.StringProperty(default='',required=True)
    story =  db.ReferenceProperty(Story, collection_name='storysteps', required=True)
    order = db.IntegerProperty(default=1)

# Tasks are urls that meet some constraints that users must develop. 
class Task(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty(default='', required=True)
    storystep =  db.ReferenceProperty(StoryStep, collection_name='challenges', required=True)
    order = db.IntegerProperty(default=1)
    url_contains = db.StringProperty(default='appspot')
    url_content_contains = db.StringProperty(default='Hello')
    url_content_does_not_contain = db.StringProperty(default='Bad Content')
    contains_game_id = db.BooleanProperty(default=False)   

    @staticmethod
    def evaluate(url, taskKey, content):
        task = Task.get(taskKey)
        passed = True
        if task.url_content_contains and task.url_content_contains not in content: 
            passed = False
        
        if task.url_content_does_not_contain and task.url_content_does_not_contain in content:
            passed = False
        
        if task.url_contains and task.url_contains not in url:
            passed = False
        return passed
    
    @staticmethod
    def fetch_content(url, taskKey = None):
        params = urllib.urlencode({'test': "test"})
        try:
            request_time = datetime.datetime.now()
            deadline = 10
            result = urlfetch.fetch(url=url,
                                payload=params,
                                method=urlfetch.POST,
                                deadline=deadline,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response_time = datetime.datetime.now()
            logging.info("headers %s", result.headers)
            logging.info("result content %s", result.content)
            delta = response_time - request_time
            request_microseconds = delta.seconds * 1000000 + delta.microseconds
            status = result.status_code
            passed = True
            #Todo: Check status code before evaluating contents
            if taskKey:
                passed = Task.evaluate(url=url,
                                               taskKey=taskKey,
                                               content = result.content)
            
            return True, passed, result.content #url_fetchable, passed, content
            
        except Exception, e:
            logging.info("Not catching exceptions yet. %s", str(e))
            return False, False, str(e)


# Videos in StorySteps and appear in some order. 
# Videos can be locked until all the Tasks of lower order (0,1,2) are accomplished.  
class Video(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty(default='', required=True)
    storystep =  db.ReferenceProperty(StoryStep, collection_name='videos', required=True)
    url = db.StringProperty(default='http://www.youtube.com/watch?v=pRpeEdMmmQ0')
    order = db.IntegerProperty(default=1)
	
# A game is used to keep track of a user's progress in a game. 
# Users can save and restart their games
# Show game progress for a story by tag to see everyone that is playing. Only show tasks. 
class Game(db.Model):
	name = db.StringProperty(required=True)
	story =  db.ReferenceProperty(Story, collection_name='games', required=True)
	owner = db.ReferenceProperty(User, collection_name='games', required=True)

# TaskUnlocks are used to keep track if a user has unlocked a task in a specific game. 
class TaskUnlock(db.Model):
	game =  db.ReferenceProperty(Game, collection_name='taskunlocks', required=True)
	task =  db.ReferenceProperty(Task, collection_name='taskunlocks', required=True)


