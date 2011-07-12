import liverest as rest
import logging
import base64
import models

#from google.appengine.ext import webapp
import webapp2 as webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json


class ActionHandler(webapp.RequestHandler):
    def my_custom_method(self):
        self.response.write('Hello, custom method world!')
        
    def time_check(self, year, month):
        self.response.write('The year is: %s and the month is: %s' % (year, month) )
        
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
