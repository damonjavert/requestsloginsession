"""
Run tests
"""
import pytest

from requestsloginsession import RequestsLoginSession

def test_login_session() -> None:
    """
    Use httpbingo.org to test that cookie data is saved and retrieved from the pickle file session_file
    """

    # Create initial session
    login_url = "http://httpbingo.org/basic-auth/user123/passwd123"
    login_data = {'username' : 'user123', 'password' : 'passwd123' }
    session_initial = RequestsLoginSession(login_url=login_url, login_data=login_data, force_login=True)
    login_session_initial = session_initial.retrieve_content("http://httpbingo.org/cookies/set?k1=v1234&k2=v5678")
    assert login_session_initial.status_code == 200  # Test that httpbingo is actually working

    # Create second session that retrieves the session data from the pickle file
    session_two = RequestsLoginSession(login_url=login_url, login_data=login_data)
    login_session_two = session_two.retrieve_content("http://httpbingo.org/cookies")
    assert login_session_initial.status_code == 200  # Test that httpbingo is actually working
    assert login_session_two.json() == {'k1': 'v1234', 'k2': 'v5678'}


@pytest.mark.skip(reason="No mock server for http post logins setup yet")
# We would also need to get the status_code attribute from RequestsLoginSession() to avoid calls like shown here,
# which is not currently supported
def test_login_failure() -> None:
    """
    Test a 403 when a deliberately incorrect credentials are supplied

    :return: None
    """

    login_url = "http://mockhttppostlogin.example"
    login_data = {'username' : 'user123WRONG', 'password' : 'passwd123WRONG' }
    session_login_failure = RequestsLoginSession(login_url=login_url, login_data=login_data, force_login=True)
    test_session_failure = session_login_failure.retrieve_content("http://mockhttppostlogin.example/posts")
    assert test_session_failure.status_code == 401


@pytest.mark.skip(reason="No mock server for http post logins setup yet")
def test_login_success() -> None:
    """
    Use httpbingo.org to test a 200 when correct credentials are supplied

    :return: None
    """

    login_url = "http://mockhttppostlogin.example"
    login_data = {'username' : 'user123', 'password' : 'passwd123' }
    session_login_success = RequestsLoginSession(login_url=login_url, login_data=login_data, force_login=True)
    test_session_success = session_login_success.retrieve_content("http://mockhttppostlogin.example/posts")
    assert test_session_success.status_code == 200
