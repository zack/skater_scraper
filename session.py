import cookielib
import urllib
import urllib2
import getpass

# The purpose of this file is to log in and get the session_id.
# This is used by start.py so that at the beginning of every run an
# updated session id is captured for use with every request in the script.
# To use, just updated lines 31-32 with your login info.

# -> [urllib2.Response, cookielib.cookieJar]
# Logs in and returns the response and cookies
def log_in():

  # Store the cookies and create an opener that will hold them
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  # Add headers
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]

  # Install opener (note that this changes the global opener to the one
  # we just made, but you can also just call opener.open() if you want)
  urllib2.install_opener(opener)

  # The action/ target from the form
  authentication_url = 'https://wftda.com/login'

  # Get login info from user
  usernm = raw_input('Email: ')
  passwd = getpass.getpass('Password: ')

  # Input parameters we are going to send
  payload = {
        'submitButton': '',
        'Login-Email': usernm,
        'Login-Password': passwd
      }

  # Use urllib to encode the payload
  data = urllib.urlencode(payload)

  # Build our Request object (supplying 'data' makes it a POST)
  req = urllib2.Request(authentication_url, data)

  # Make the request and read the response
  resp = urllib2.urlopen(req)
  return [resp, cj]

# -> String
# Logs in and returns the session id
def get_session_id():
  response = log_in()
  cookies = response[1]._cookies
  session_id = cookies['wftda.com']['/']['wftda_session'].value
  return session_id
