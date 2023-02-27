"""
requestsloginsession is a simple wrapper for requests.Session() that savesthe data locally via pickle
to allow session information to be recalled on subsequent script runs without needing to relogin.
All the attributes from requests are available.
"""
import logging
import pickle
import datetime
import os
from urllib.parse import urlparse
import requests

logger = logging.getLogger('main.' + __name__)

# Example usage
#
# login_url = "https://website.com/login.php"
# login_test_url = "https://website.com"
# login_test_string = "Latest dig pics..."
# login_data = {'username' : 'userstr', 'password' : 'passstr' }
#
# mywebsitesession = RequestsLoginSession(loginUrl, loginData, loginTestUrl, successStr)
# resource = mywebsitesession.retrieve_content("https://website.com/cutedogpics")
# print(resource.text)


class RequestsLoginSession:
    """
    A wrapper for requests.Session() that saves the data locally via pickle to allow session information
    to be recalled on subsequent script runs without needing to relogin.

    Originally based on: https://stackoverflow.com/a/37118451/2115140
    Originally by: https://stackoverflow.com/users/1150303/domtomcat
    """
    # pylint: disable=too-many-instance-attributes
    # Explicit is always better than implicit. Although listing all the parameters in the __init__ method head may look cumbersome,
    # we are explicit about what parameters the users need to specify when they create instance objects.
    # https://betterprogramming.pub/6-best-practices-for-defining-the-initialization-method-in-python-9173808bfb8f"

    def __init__(self,
                 # pylint: disable=too-many-arguments
                 # The class requires all these options and as it is called by other external modules the functionality
                 # cannot be refactored to reduce them.
                 login_url: str,
                 login_data: dict,
                 login_test_url: str = None,
                 login_test_string: str = None,
                 test_login: bool = False,
                 session_file_appendix: str = '_session.dat',
                 max_session_time_seconds: int = 30 * 60,
                 proxies: dict = None,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                 force_login: bool = False) -> None:
        """
        Create or use an existing login session

        :param login_url: URL used to login to the site to setup the session
        :param login_data: Credentials to access the URL in the format of: {'username' : 'userstr', 'password' : 'passstr' }
        :param login_test_url: URL used to test that the login has succeeded
        :param login_test_string: String to search for in the output of login_test_url to ascertain if the login as succeeded
        :param test_login: Perform a login test with login_test_url and login_test_string
        :param session_file_appendix: Specify a custom name to store session information
        :param max_session_time_seconds: Create a new requests.Session() and do not use the session_file after this time
        :param proxies: Use an http or https proxy for all traffic in the format of: { 'https' : 'https://user:pass@server:port', 'http' : '...' }
        :param user_agent: Specify the user agent request header to be used for all requests.
        :param force_login: Create a new requests.Session() and do not check for a session_file to use
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
        self.force_login = force_login

        self.session = None

        self.login()
        if test_login:
            self.test_login()

    def modification_date(self, filename: str) -> datetime:
        """
        return last file modification date as datetime object
        """
        file_mtime = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(file_mtime)

    def login(self) -> None:
        """
        login to a session. Try to read last saved session from cache file. If this fails
        do proper login. If the last cache access was too old, also perform a proper login.
        Always updates session cache file.
        """

        if self.determine_use_cache():
            self.session = self.load_session_from_cache()
        else:
            self.session = self.create_new_session()

    def test_login(self) -> None:
        """
        Test the login by navigating to a specific login_test_url and searching for the str login_test_string
        """
        logger.debug('Loaded session from cache and testing login...')
        resource = self.session.get(self.login_test_url)

        if self.login_test_string.lower() not in resource.text.lower():
            os.remove(self.session_file)  # Delete the session file if login fails
            raise RuntimeError(f"Could not log into provided site - {self.login_url} - successful login string not found")
        if 'Your username or password was incorrect.' in resource.text:
            raise RuntimeError(f"Could not log into provided site {self.login_url} - username or password was incorrect")

    def determine_use_cache(self) -> bool:
        """
        Determine if the cache file self.session_file should be used

        :param: bool: true if to always login regardless of the age of the self.session_file
        :return: bool: True if it should be used, false otherwise
        """
        if self.force_login:
            return True

        if not os.path.exists(self.session_file):
            return False

        session_file_mod_time = self.modification_date(self.session_file)
        last_modification = (datetime.datetime.now() - session_file_mod_time).seconds

        if last_modification < self.max_session_time_seconds:
            return True

        return False

    def save_session_to_cache(self) -> None:
        """
        Save session to a cache file self.session_file
        """
        session_file = self.session_file
        # always save (to update timeout)
        with open(session_file, "wb") as session_file_object:
            pickle.dump(self.session, session_file_object)
            logger.debug('updated session cache-file %s', session_file)

    def load_session_from_cache(self) -> pickle:
        """
        Load session into from the cache file
        :return: pickle: cache data from self.session_file
        """
        with open(self.session_file, "rb") as session_file_object:
            return pickle.load(session_file_object)

    def create_new_session(self) -> callable(requests.Session()):
        """
        Create a new requests.Session() and add user_agent header
        :return: requests.Session()
        """
        _session = requests.Session()
        _session.headers.update({'user-agent': self.user_agent})
        _session.post(self.login_url, data=self.login_data, proxies=self.proxies)
        logger.debug('Created new session with login')
        self.save_session_to_cache()

        return _session

    def retrieve_content(self, url: str, method: str = "get", post_data=None, post_data_files=None, **kwargs) -> callable(requests.Session()):
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
