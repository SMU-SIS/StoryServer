'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
from tournament import models

#import urllib
#import datetime
#from google.appengine.api import urlfetch
#from google.appengine.api import memcache
#from time import sleep
#from xxx import models
#from xxx import views

class Test_Models(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        for x in models.User.all(): x.delete()
        
    def test_user_creation(self):  
        self.assertEqual(1, 1)
        user = models.User(user_id ='Bob').save()
        results = models.User.all()
        self.assertEqual(results.count(),1)

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
        
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
