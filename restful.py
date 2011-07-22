import liverest as rest
import logging
import base64
import models
import datetime
import urllib

#from google.appengine.ext import webapp
import webapp2 as webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

from django.utils import simplejson as json


class ActionHandler(webapp.RequestHandler):

    def fetch_content(self,url):
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
			return True, result.content
		    
        except Exception, e:
			logging.info("Not catching exceptions yet. %s", str(e))
			return False, str(e)

	def my_custom_method(self):
		self.response.write('Hello, custom method world!')
        
    def time_check(self, year, month):
        self.response.write('The year is: %s and the month is: %s' % (year, month) )
    
    def check_url(self, url=None, contains=None):
		url = self.request.get("url")
		contains = self.request.get("contains")
		doesnotcontain = self.request.get("doesnotcontain")
		url_contains = self.request.get("url_contains")
		
		format = self.request.get("format")
		url_fetchable, content = self.fetch_content(url)
		passed = True
		if contains and contains not in content: 
			passed = False
		
		if doesnotcontain and doesnotcontain in content:
			passed = False
		
		if url_contains and url_contains not in url:
			passed = False
		
		if format=="plain":	
		  self.response.write('Checked <br>url=%s <br>url fetchable=%s <br>url_contains=%s <br>contains=%s <br>does not contain=%s <br>passed=%s <br> Contents were: <hr> %s' % (url, url_fetchable, url_contains, contains, doesnotcontain, passed, content) )
		else:
			resultDict = {"passed":passed,
						  "url": url,
						  "url_fetchable": url_fetchable,
						  "contains":contains,
						  "doesnotcontain": doesnotcontain,
						  "url_contains" : url_contains,
						  "content":content}
        	
 			self.response.headers['Content-Type'] = 'application/json'
			self.response.out.write(json.dumps(resultDict))       
        
    def get_current_user(self):
        user = models.User.get_user(self.request)
        #user = get_user(self.request)
        if user:
            userDict = {"nickname": user.nickname,"key": str(user.key())}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(userDict))
        else:
            userDict = {"error" : "No user logged in"}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(userDict)) 
        
application = webapp.WSGIApplication([
    webapp.Route('/rest/<year:\d{4}>/<month:\d{2}>', handler=ActionHandler, name='blog-archive', handler_method='time_check'),
    webapp.Route('/rest/my_custom_method', handler=ActionHandler, name='custom-1', handler_method='my_custom_method'),
    webapp.Route('/rest/action/get_current_user', handler=ActionHandler, name='get_current_user', handler_method='get_current_user'),
    #webapp.Route('/rest/action/check_url/<url>/contains/<contains>', handler=ActionHandler, name='check_url', handler_method='check_url'),
	webapp.Route('/rest/action/check_url', handler=ActionHandler, name='check_url', handler_method='check_url'),
    
    #Send all other /rest requests to default rest dispatcher. 
    ('/rest.*', rest.Dispatcher)],
    debug=True)

class OwnerAuthorizer(rest.Authorizer):
     
    #If model contains email, you can prevent reads by non-owners.
    #For writes, if the model contains the method, verify_before_update(), you could call that before updating.         
	def filter_read(self, dispatcher, models):
		return self.filter_models(models)
	
	def filter_models(self, models):
		for model in models:
			if hasattr(model, 'email'):
				model.email = 'PRIVATE'
		return models


rest.Dispatcher.base_url = '/rest'
rest.Dispatcher.authorizer = OwnerAuthorizer()
rest.Dispatcher.add_models_from_module(models)

#rest.Dispatcher.add_models({
#  "Competition": (models.Competition, ['GET_METADATA', 'GET', 'POST', 'PUT']),
#  "App": (models.App, ['GET_METADATA', 'GET', 'POST', 'PUT']),
#  "Tournament":(models.Tournament, ['GET_METADATA', 'GET', 'POST', 'PUT']), 
#  "TournamentHeat":(models.TournamentHeat, ['GET_METADATA', 'GET', 'POST', 'PUT']), 
#  "Game": (models.Game, ['GET_METADATA', 'GET', 'POST', 'PUT']),
#  "GameType":(models.GameType, ['GET_METADATA', 'GET', 'POST', 'PUT'])})

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
