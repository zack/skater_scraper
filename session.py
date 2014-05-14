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

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # User agent just in case
    opener.addheaders = [(
        'User-agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit'
        '/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    )]

    urllib2.install_opener(opener)

    authentication_url = 'https://wftda.com/login'

    usernm = raw_input('Email: ')
    passwd = getpass.getpass('Password: ')

    payload = {
        'submitButton': '',
        'Login-Email': usernm,
        'Login-Password': passwd
    }

    data = urllib.urlencode(payload)
    req = urllib2.Request(authentication_url, data)
    resp = urllib2.urlopen(req)

    if resp.headers.get("Content-Length", 0) == 0:
        print "Login failed."
        exit

    # Return response and cookies for future request authentication
    return [resp, cj]

# -> String
# Logs in and returns the session id
def get_session_id():
    response = log_in()
    cookies = response[1]._cookies
    session_id = cookies['wftda.com']['/']['wftda_session'].value
    return session_id
