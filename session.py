import cookielib
import urllib
import urllib2
import getpass

# For Session Management

class SessionManager:
    AUTHENTICATION_URL = 'https://wftda.com/login'

    # ->
    # Logs in and sets the response object
    def __init__(self):
        self.generate_opener()

        while True:
            self.authenticate()
            resp = self.update_cookie()
            if resp.headers.get("Content-Length", 0) == 0:
                print "Login failed. Try again?"
            else:
                print "Login successful!"
                break

    # Generates the opener to be used for future requests
    # ->
    def generate_opener(self):
        global cookiejar
        cookiejar = cookielib.CookieJar()
        opener = urllib2.build_opener(
                                    urllib2.HTTPCookieProcessor(cookiejar)
                                )

        # User agent just in case
        opener.addheaders = [(
            'User-agent',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit'
            '/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        )]

        urllib2.install_opener(opener)

    # Gets login data from user and sets auth_payload
    # ->
    def authenticate(self):
        global auth_payload
        usernm = raw_input('Email: ')
        passwd = getpass.getpass('Password: ')
        auth_payload = {
            'submitButton': '',
            'Login-Email': usernm,
            'Login-Password': passwd
        }

    # -> String
    # Logs in and returns the session id
    def get_session_id(self):
        session_id = cookiejar._cookies['wftda.com']['/']['wftda_session'].value
        return session_id

    # Updates the cookie with existing authentication data
    def update_cookie(self):
        data = urllib.urlencode(auth_payload)
        req = urllib2.Request(SessionManager.AUTHENTICATION_URL, data)
        resp = urllib2.urlopen(req)

        return resp
