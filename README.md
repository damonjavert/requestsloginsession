# requestsloginsession

![GitHub last commit](https://img.shields.io/github/last-commit/damonjavert/requestsloginsession) ![License](https://img.shields.io/github/license/damonjavert/requestsloginsession) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

`requestsloginsession` is a simple wrapper for `requests.Session()` that saves the data locally via pickle to allow session information to be recalled on subsequent script runs without needing to relogin. All the attributes from `requests` are available.

## Example usage

```
>>> from requestsloginsession import RequestsLoginSession
>>> login_url = "http://httpbingo.org/basic-auth/user123/passwd123"
>>> login_data = {'username' : 'user123', 'password' : 'passwd123' }
>>> mysession = RequestsLoginSession(login_url, login_data)
>>> r = mysession.retrieve_content("http://httpbingo.org/cookies/set?k1=v1234&k2=v5678")
>>>
 $ file httpbingo.org_session.dat
httpbingo.org_session.dat: data
 $ python3

>>> from requestsloginsession.requestsloginsession import RequestsLoginSession
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

