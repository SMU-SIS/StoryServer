from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from django.utils import simplejson
import models

import logging
import urllib

import Cookie
import re
import base64
from myutil import common

class RPXData(db.Model):
    janrainID = db.StringProperty(required=True)
    auth_url = db.StringProperty(required=True)
    api_key = db.StringProperty(required=True)
    #loginURL = db.StringProperty(required=True)
    base_token_url = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
     
    @staticmethod
    def get_rpx_data():
        rpx = RPXData.all().order('created').get()
        if not rpx:
            janrainID = 'pivotalexpert'
            auth_url = 'https://rpxnow.com/api/v2/auth_info'
            api_key = '89ce5416ddbd4d41e021fe8ccd0d3091c6a98a6f'
            #loginURL = 'https://pivotalexpert.rpxnow.com/openid/v2/signin?token_url=http%3A%2F%2Fdeli.appspot.com%2Frpx.php'
            base_token_url = '/rpx.php'  #'http://deli.appspot.com/rpx.php'
            rpx = RPXData(janrainID = janrainID,
                          auth_url=auth_url,
                          api_key = api_key,
                          # tokenURL = tokenURL,
                          base_token_url= base_token_url)                             
            rpx.put()
            #Create a default rpx entry, save it, and return it. 
        return rpx
     
    @staticmethod
    def get_janrain_id():
        rpxdata = RPXData.get_rpx_data()
        return rpxdata.janrainID
 
    @staticmethod
    def get_api_key():
        rpxdata = RPXData.get_rpx_data()
        return rpxdata.api_key
        #return '89ce5416ddbd4d41e021fe8ccd0d3091c6a98a6f'
                
    @staticmethod
    def get_auth_url():
        rpxdata = RPXData.get_rpx_data()
        return rpxdata.auth_url
        #return 'https://rpxnow.com/api/v2/auth_info'
 
    @staticmethod
    def get_token_url(domain_url):
        rpxdata = RPXData.get_rpx_data()
        return domain_url+rpx.base_token_url
    
    @staticmethod
    def get_login_url(domain_url):
        rpxdata = RPXData.get_rpx_data()
        return 'https://'+ rpxdata.get_janrain_id() +'.rpxnow.com/openid/v2/signin?token_url='+domain_url+'/rpx.php'   
    
class RPXTokenHandler(webapp.RequestHandler):
  def get(self):
    logging.info('RPXTokenHandler.get start')

  def post(self):
    logging.info('RPXTokenHandler.post start')
    token = self.request.get('token')
    logging.info('token: '+str(token))
    url = RPXData.get_auth_url() #'https://rpxnow.com/api/v2/auth_info'
    args = {
      'format': 'json',
      'apiKey': RPXData.get_api_key(),#'89ce5416ddbd4d41e021fe8ccd0d3091c6a98a6f',
      'token': token
      }
    logging.info('calling url: '+str(url))
    r = urlfetch.fetch(url=url,
                       payload=urllib.urlencode(args),
                       method=urlfetch.POST,
                       headers={'Content-Type': 'application/x-www-form-urlencoded'}
                       )
    logging.info('response: '+str(r.content))
    json = simplejson.loads(r.content)
    logging.info('json response: '+str(json))
    if json['stat'] == 'ok':   
      unique_identifier = str(json['profile']['identifier'])
      nickname = None
      if 'preferredUsername' in json['profile']:
          nickname = json['profile']['preferredUsername']
      email = None
      if 'email' in json['profile']:
          email = json['profile']['email']
      if nickname:
          nickname = str(nickname)
      if email:
          email = str(email)

      logging.info('rpx login successful, unique_identifier: '+str(unique_identifier)+', nickname: '+str(nickname)+', email: '+str(email))
      # log the user in using the unique_identifier
      # this should your cookies or session you already have implemented
      self.log_user_in(user_id=unique_identifier, nickname=nickname, email=email)
      logging.info('login successful, redirect to /login/')
#      self.redirect('/profile/%s' % unique_identifier)
      self.redirect('/gui/rest-test.html')
    else:
      logging.error('there was an error in rpx login')
      self.redirect('/')

  def log_user_in(self, user_id, nickname=None, email=None):
    user = models.User.login(user_id=user_id, nickname=nickname, email=email)
    session_id = models.Session.create_session_for_user(user_id)
    addCookie(self, name = 'session_id', value = session_id)

class LogoutHandler(webapp.RequestHandler):
  def get(self):
    logging.info('LogoutHandler.get start')
    self.do(self.request)
  
  def post(self):
    logging.info('LogoutHandler.post start')
    self.do(self.request)
  
  def do(self, request):
    try:
        logging.info('cookies: '+str(self.request.cookies))
        id = self.request.cookies['session_id']
        id = base64.b64decode(id)
        db.delete(db.Key.from_path(models.Session.kind(), long(id)))
    except Exception, e:
        logging.warning('Error while deleting session: '+str(e))
    
    addCookie(self, name = 'session_id', value = '', expires = -100000)
    target = request.get('target')
    if not target:
      target = '/'
    self.redirect(target)

def addCookie(handler, name, value, expires = 86400, domain = None, path = '/'):
  logging.info('addCookie, handler: '+str(handler)+', name: '+str(name)+', value: '+str(value)+\
               ', expires: '+str(expires)+', domain: '+str(domain)+', path: '+str(path))
  if domain == None:
    domain = common.getDomainName(handler.request)

  simpleCookieObj = Cookie.SimpleCookie()

  simpleCookieObj[name] = str(base64.b64encode(str(value)))
  simpleCookieObj[name]['expires'] = expires
  simpleCookieObj[name]['path'] = path
  simpleCookieObj[name]['domain'] = domain
  simpleCookieObj[name]['secure'] = ''

  #Cookie.SimpleCookie's output doesn't seem to be compatible with WebApps's http header functions
  #and this is a dirty fix

  headerStr = simpleCookieObj.output()
  logging.info('add cookie: '+str(headerStr))
  regExObj = re.compile('^Set-Cookie: ')
  handler.response.headers.add_header('Set-Cookie', str(regExObj.sub('', headerStr, count=1)))


application = webapp.WSGIApplication(
                                     [('/rpx.php', RPXTokenHandler),
                                      ('/logout', LogoutHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
