'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
import models

#import urllib
#import datetime
#from google.appengine.api import urlfetch
#from google.appengine.api import memcache
#from time import sleep
#from xxx import models
#from xxx import views

class Test_Models(unittest.TestCase):

    def setUp(self):
        self.user =  models.User(user_id ='Test User').save()
        self.story =  models.Story(name = 'Test Story', owner = self.user).save()
        self.storysteps = []
        for x in range(2):
            story =  models.StoryStep(name = 'Test Story Step '+str(x),
                                  description = 'Test Story Step Description',
                                  story = self.story,  
                                  order = x).save()
            self.storysteps.append(story)
        
    def tearDown(self):
        for x in models.StoryStep.all(): x.delete()
        for x in models.Story.all(): x.delete()
        for x in models.User.all(): x.delete()
                
    def test_user_creation(self):  
        user = models.User(user_id ='Bob').save()
        results = models.User.all()
        self.assertEqual(2, results.count())
        
    def test_get_current_user(self):
    	userKey = models.User(user_id ='Bob').save()
    	user = models.User.get(userKey)
    	result = user.get_current_user(user_id=None, nickname='Bob', email='Bob@test.com') 
    	self.assertEqual(None, result)
    	
    	#If existing user then fetch the users. 
    	result = user.get_current_user(user.user_id, nickname='John', email='John@test.com')         
        self.assertEqual(user.nickname, result.nickname)
        
        #If no user with the id create a user.
    	result = user.get_current_user('99', nickname='John', email='John@test.com') 
        self.assertEqual('John', result.nickname)
    
    #This can be changed to test as static
    def test_user_login(self):
        userKey = models.User(user_id ='Bob').save()
    	user = models.User.get(userKey)
    	result = models.User.login(user.user_id)
    	self.assertEqual(user.nickname, result.nickname)
    	
    def test_user_is_current_user_admin(self):
    	self.assertEqual(False, models.User.is_current_user_admin())
    	    
    def test_create_logout_url(self): 
        self.assertEqual('/logout?target=myTarget', models.User.create_logout_url('myTarget')) 
 
    def test_create_login_url(self): 
        self.assertEqual('/login?target=myTarget', models.User.create_login_url('myTarget')) 
        
    def test_create_delete_sesson_for_user(self):
        self.assertEqual(0, models.Session.all().count())      
        sessionID = models.Session.create_session_for_user(user_id='99')
        self.assertEqual(1, models.Session.all().count())
        
        result = models.Session.get_session(sessionID)
        self.assertEqual(sessionID, result.key().id())
        
        models.Session.delete_session_for_user('99')
        self.assertEqual(0, models.Session.all().count())      

    def test_user_tag(self):
        self.assertEqual(0, models.UserTag.all().count())      
        userTag =  models.UserTag(user = self.user, tag='Test Tag').save()
        self.assertEqual(1, models.UserTag.all().count())     

    def test_create_story(self):
        self.assertEqual(1, models.Story.all().count())      
        story =  models.Story(name = 'Test Story', owner = self.user).save()
        self.assertEqual(2, models.Story.all().count())  
 
    def test_create_story_step(self):
        self.assertEqual(2, models.StoryStep.all().count())      
        story =  models.StoryStep(name = 'Test Story Step 3',
                                  description = 'Test Story Step Description',
                                  story = self.story,  
                                  order = 3).save()
        self.assertEqual(3, models.StoryStep.all().count())  
 
    def test_create_task(self):
        self.assertEqual(0, models.Task.all().count())      
        task =  models.Task(name = 'Test Task 3',
                             description = 'Test Task Description',
                             storystep = self.storysteps[0],  
                             order = 3).save()
        self.assertEqual(1, models.Task.all().count())         
 
    def test_check_url_for_task(self):
        url = 'http://storyserver1.appspot.com/rest/metadata'
        task =  models.Task(name = 'Test URL Check Task',
                             description = 'Test Task Description',
                             storystep = self.storysteps[0],  
                             order = 3,
                             url_contains = 'Singpathhhh').save()
        url_fetchable, passed, content = models.Task.fetch_content(url)
        self.assertEqual(True, url_fetchable) 
        self.assertEqual(True, passed)
        
        #Add test to check for url_contains
        #Add test to check for url_content_contains
        #Add test to check for url_content_does_not_contain
        #Add test to check for contains_game_id      
                
    temp = '''      

# Stories consist of an ordered collection of StorySteps

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
     
'''        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
