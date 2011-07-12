import re
import datetime
import base64
import logging

def getDomainName(request):
    if type(request) != type(''):
        domain = request.host_url
    else:
        domain = request
    domain = domain.replace('https://', '').replace('http://', '')
    domain = re.sub(':[0-9]+', '', domain)
    return domain

def getHostURI(request):
    uri = request.build_absolute_uri('/')
    if uri[-1:] == '/':
        uri = uri[0 : len(uri) - 1]
    return uri

def get_parameter_from_request(request, parameterName, defaultValue=None, post=True, get=True):
    result = defaultValue
    if post and (parameterName in request.POST): result = request.POST.get(parameterName)
    elif get and (parameterName in request.GET): result = request.GET.get(parameterName)
    return result

def str_to_date(str):
    if str:
        try:
            result = datetime.datetime.strptime(str, '%Y-%m-%d')
        except:
            result = datetime.datetime.strptime(str, '%d/%m/%Y')
        return datetime.date(result.year, result.month, result.day)
    return None


def set_cookie(response, name, value, expires = 86400, domain = None, path = '/'):
    logging.info('set_cookie, name: '+str(name)+', value: '+str(value)+\
                 ', expires: '+str(expires)+', domain: '+str(domain)+', path: '+str(path))
    response.set_cookie(key = name, value = str(base64.b64encode(value)), max_age = expires, domain = domain, path = path, secure = None)
