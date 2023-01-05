import logging
import pickle
import datetime
import os
from urllib.parse import urlparse
import requests

logger = logging.getLogger('main.' + __name__)

# Example usage
#
# loginUrl = "https://website.com/login.php"
# loginTestUrl = "https://website.com"
# successStr = "Latest dig pics..."
# loginData = {'username' : 'userstr', 'password' : 'passstr' }
#
# mywebsitesession = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)
# resource = mywebsitesession.retrieve_content("https://website.com/cutedogpics")
# print(resource.text)


class MyLoginSessionTest:
    """
    Taken from: https://stackoverflow.com/a/37118451/2115140
    New features added
    Originally by: https://stackoverflow.com/users/1150303/domtomcat

    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintains a cache-file for restoring session data from earlier
    script executions.
    """

    def __init__(self,
                 login_url,
                 login_data,
                 login_test_url,
                 login_test_string,
                 test_login=False,
                 session_file_appendix='_session.dat',
                 max_session_time_seconds=30 * 60,
                 proxies=None,
                 user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                 force_login=False,
                 **kwargs):
        """
        save some information needed to login the session

        you'll have to provide 'loginTestString' which will be looked for in the
        responses html to make sure, you've properly been logged in

        'proxies' is of format { 'https' : 'https://user:pass@server:port', 'http' : ...
        'loginData' will be sent as post data (dictionary of id : value).
        'maxSessionTimeSeconds' will be used to determine when to re-login.
        """
        url_data = urlparse(login_url)

        self.proxies = proxies
        self.login_data = login_data
        self.login_url = login_url
        self.login_test_url = login_test_url
        self.max_session_time_seconds = max_session_time_seconds
        self.session_file = url_data.netloc + session_file_appendix
        self.user_agent = user_agent
        self.login_test_string = login_test_string

        self.login(force_login, test_login, **kwargs)

    def modification_date(self, filename):
        """
        return last file modification date as datetime object
        """
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def login(self, force_login=False, test_login=False, **kwargs):
        """
        login to a session. Try to read last saved session from cache file. If this fails
        do proper login. If the last cache access was too old, also perform a proper login.
        Always updates session cache file.
        """
        read_from_cache = False
        # logger.debug('loading or generating session...')
        if os.path.exists(self.session_file) and not force_login:
            time = self.modification_date(self.session_file)

            # only load if file less than maxSessionTimeSeconds old
            last_modification = (datetime.datetime.now() - time).seconds
            if last_modification < self.max_session_time_seconds:
                with open(self.session_file, "rb") as f:
                    self.session = pickle.load(f)
                    read_from_cache = True
                    # logger.debug("loaded session from cache (last access %ds ago) " % last_modification)
        if not read_from_cache:
            self.session = requests.Session()
            self.session.headers.update({'user-agent': self.user_agent})
            res = self.session.post(self.login_url, data=self.login_data,
                                    proxies=self.proxies, **kwargs)
            logger.debug('created new session with login')
            self.save_session_to_cache()

        if test_login:
            logger.debug('Loaded session from cache and testing login...')
            res = self.session.get(self.login_test_url)
            if self.login_test_string.lower() not in res.text.lower():
                os.remove(self.session_file)  # Delete the session file if login fails
                raise Exception(f"Could not log into provided site - {self.login_url} - successful login string not found")
            if 'Your username or password was incorrect.' in res.text:
                raise Exception(f"Could not log into provided site {self.login_url}  - username or password was incorrect")

    def save_session_to_cache(self):
        """
        save session to a cache file
        """
        # always save (to update timeout)
        with open(self.session_file, "wb") as f:
            pickle.dump(self.session, f)
            logger.debug('updated session cache-file %s' % self.session_file)

    def retrieve_content(self, url, method="get", post_data=None, post_data_files=None, **kwargs):
        """
        return the content of the url with respect to the session.

        If 'method' is not 'get', the url will be called with 'postData'
        as a post request.
        """
        if method == 'get':
            res = self.session.get(url, proxies=self.proxies, **kwargs)
        else:
            res = self.session.post(url, data=post_data, proxies=self.proxies, files=post_data_files, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.save_session_to_cache()

        return res

