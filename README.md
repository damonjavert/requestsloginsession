# RequestsLoginSession

![PyPI](https://img.shields.io/pypi/v/requestsloginsession) ![PyPI - Status](https://img.shields.io/pypi/status/requestsloginsession) ![PyPI - Downloads](https://img.shields.io/pypi/dm/requestsloginsession) ![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/damonjavert/requestsloginsession) ![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/damonjavert/requestsloginsession) ![Pylint status](https://github.com/damonjavert/requestsloginsession/actions/workflows/pylint.yml/badge.svg) ![GitHub last commit](https://img.shields.io/github/last-commit/damonjavert/requestsloginsession) ![License](https://img.shields.io/github/license/damonjavert/requestsloginsession) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

`requestsloginsession` is a simple wrapper for `requests.Session()` that saves the data locally via pickle to allow session information to be recalled on subsequent script runs without needing to relogin. All the attributes from `requests` are available.

## Install

From PyPi:
```
pip install requestsloginsession
```
Or use the latest commit:
```
git clone https://github.com/damonjavert/requestsloginsession.git
cd requestsloginsession
python setup.py install
```

## Features

* Saves cookie data to a local file via `pickle` and uses it to send cookie data in subsequent requests.
* Cookie data saved has an expiry time - `max_session_time_seconds`, after which `requestsloginsession` will not send it, or you can force it not to be used with `force_login`.
* Login success can be tested with a specific URL - `login_test_url` and string - `login_test_string` to be found on the page.
* A proxy can be used.
* Customisable `user_agent` string.

## Example usage

```python
>>> from requestsloginsession import RequestsLoginSession
>>> login_url = "http://httpbingo.org/basic-auth/user123/passwd123"
>>> login_data = {'username' : 'user123', 'password' : 'passwd123' }
>>> mysession = RequestsLoginSession(login_url, login_data)
>>> r = mysession.retrieve_content("http://httpbingo.org/cookies/set?k1=v1234&k2=v5678")
>>>
 $ file httpbingo.org_session.dat
httpbingo.org_session.dat: data
 $ # We have now exited python, when we start a new interpreter we can request httpbingo
 $ # to show our cookies and the `k1=v1234&k2=v5678` data will now be shown:
 $ python3

>>> from requestsloginsession import RequestsLoginSession
>>> login_url = "http://httpbingo.org/basic-auth/user123/passwd123"
>>> login_data = {'username' : 'user123', 'password' : 'passwd123' }
>>> mysession = RequestsLoginSession(login_url, login_data)
>>> r = mysession.retrieve_content("http://httpbingo.org/cookies")
>>> r.json()
{'k1': 'v1234', 'k2': 'v5678'}
>>> r.status_code
200
>>> r.text
'{\n  "k1": "v1234",\n  "k2": "v5678"\n}\n'
```

## FAQ

### Why not just use `requests.Session()` directly?
Of course you can do, but this module makes life easier by handling the cookie data for you and allowing the cookie data to survive multiple runs of your script, so you do not need to relogin each time.

### I have an API key for the site I am requesting, do I still need to use this?
No, you probably do not. This module is designed to access sites where you need to authenticate before you can access it. Any modern API does not need this and you send an API key in each request. - If you have an API key you can just use `requests` directly.


