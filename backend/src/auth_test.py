"""
 - auth_test.py ~ T18B - Blue
 - Testing the provided functions for auth.py
"""

import pytest
import jwt
import requests
import users
from auth import auth_login
from auth import auth_logout
from auth import auth_register
from error import InputError
import other


def create_test_user():
    """
    Assumptions:
        - auth_register is working
    """
    test_user = auth_register("testing@test.com", "12345678", "Clark", "Kent")
    token = test_user["token"]
    return token


# Function to wipe datafiles before each test
@pytest.fixture(autouse=True)
def wipe_datafiles():
    """
        - Function to wipe datafiles before each test
    """
    # Wipe before each run
    other.workplace_reset()
    yield
    # Wipe after each run
    other.workplace_reset()


# Beginning login Test Cases
@pytest.mark.integrationtest
def test_successful_login():
    """
        Assumptions:
            - auth_register is working
            - auth_logout is working
    """
    # Setup test cases
    test_user = auth_register("testing@test.com", "12345678", "Clark", "Kent")
    test_user_token = test_user["token"]
    test_user_id = test_user["u_id"]

    auth_logout(test_user_token)

    login_dict = auth_login("testing@test.com", "12345678")
    assert login_dict["u_id"] == test_user_id



@pytest.mark.integrationtest
def test_invalid_email_login():
    """
        No assumptions needed
    """
    with pytest.raises(InputError):
        auth_login("test.com", "password")
        auth_login("test@test", "password")


@pytest.mark.integrationtest
def test_no_matching_user_login():
    """
        No assumptions needed
    """
    with pytest.raises(InputError):
        auth_login("test@test.com", "password")


@pytest.mark.integrationtest
def test_incorrect_password_login():
    """
        Assumptions:
            - auth_register is working
    """
    # Setup test case
    create_test_user()

    with pytest.raises(InputError):
        auth_login("testing@test.com", "password")

# Beginning Logout Test Cases


@pytest.mark.integrationtest
def test_successful_logout():
    """
        Assumptions:
            - auth_register is working
    """
    # Setup test case
    test_user_token = create_test_user()

    logout_dict = auth_logout(test_user_token)
    assert logout_dict["is_success"] is True


@pytest.mark.integrationtest
def test_invalid_token_logout():
    """
        Assumptions:
            - auth_register is working
    """
    # Setup test case
    with pytest.raises(jwt.exceptions.DecodeError):
        logout_dict = auth_logout("RandomIncorrectToken")
        assert logout_dict["is_success"] is False


# Beginning Register Test Cases

@pytest.mark.integrationtest
def test_successful_register():
    """
        Assumptions:
            - auth_register is working
    """
    # Setup test cases
    test_user = auth_register("testing@test.com", "12345678", "Clark", "Kent")
    test_user_id = test_user["u_id"]
    test_user_token = test_user["token"]

    found = False
    users_all_dict = users.users_all(test_user_token)

    for user in users_all_dict["users"]:
        if user["u_id"] == test_user_id:
            found = True

    assert found is True


@pytest.mark.integrationtest
def test_invalid_email_register():
    """
        No Assumptions Needed
    """
    with pytest.raises(InputError):
        auth_register("test@test", "password", "Clark", "Kent")
        auth_register("test.test", "password", "Clark", "Kent")


@pytest.mark.integrationtest
def test_taken_email_register():
    """
        Assumptions:
            - auth_register is working
    """
    # Create Test case
    create_test_user()

    with pytest.raises(InputError):
        auth_register("testing@test.com", "password", "Bruce", "Wayne")


@pytest.mark.integrationtest
def test_short_password_register():
    """
        Assumptions:
            - Pasword Can be exactly 6 characters long
    """
    with pytest.raises(InputError):
        auth_register("testing@test.com", "12345", "Clark", "Kent")


@pytest.mark.integrationtest
def test_invalid_first_name_register():
    """
        Assumptions:
            - One and fifty character names is included
    """
    with pytest.raises(InputError):
        auth_register("testing@test.com", "password", "", "Kent")
        auth_register("testing@test.com", "password",
                      "haydensmithcompisjustsuperfunlikeyaylookhowmuchfunitis", "Kent")


@pytest.mark.integrationtest
def test_invalid_last_name_register():
    """
        Assumptions:
            - One and fifty character names is included
    """
    with pytest.raises(InputError):
        auth_register("testing@test.com", "password", "Clark", "")
        auth_register("testing@test.com", "password", "Clark",
                      "Imdefinietlynotsupermanbecausepeoplecanobvlyrealise")


# HTTP Tests

# Cases for auth_login
@pytest.mark.systemtest
def test_auth_login_http():
    """
        - HTTP test for auth_login
    """
    # Create a user
    data_dict = {
        "name_first": "test",
        "name_last": "testing",
        "email": "test@test.com",
        "password": "12345678"
    }
    response = requests.post(
        "http://127.0.0.1:8080/auth/register", json=data_dict)
    response_dict = response.json()

    # Logout from user:
    register_token_dict = {"token": response_dict["token"]}
    requests.post("http://127.0.0.1:8080/auth/logout",
                  json=register_token_dict)

    # auth_login() with user
    # Is this necessary or can I just use data_dict
    login_dict = {"email": "test@test.com", "password": "12345678"}
    response1 = requests.post(
        "http://127.0.0.1:8080/auth/login", json=login_dict)
    login_returned_dict = response1.json()

    # Check if token is valid by logging out with returned token from login
    login_token_dict = {"token": login_returned_dict["token"]}
    response2 = requests.post(
        "http://127.0.0.1:8080/auth/logout", json=login_token_dict)
    valid_logut_dict = response2.json()

    # If its a valid_logout, token is valid
    assert valid_logut_dict["is_success"] is True

    # if user_id matches with register and login. User_id is correct
    assert response_dict["u_id"] == login_returned_dict["u_id"]

# Tests for auth_logout
@pytest.mark.systemtest
def test_auth_logout_http():
    """
        - HTTP test for auth_logout
    """
    # Create a user
    data_dict = {
        "name_first": "test",
        "name_last": "testing",
        "email": "test@test.com",
        "password": "12345678"
    }
    response = requests.post(
        "http://127.0.0.1:8080/auth/register", json=data_dict)
    response_dict = response.json()

    # Check if logout is successful:
    register_token_dict = {"token": response_dict["token"]}
    response1 = requests.post(
        "http://127.0.0.1:8080/auth/logout", json=register_token_dict)
    valid_logout_dict = response1.json()

    assert valid_logout_dict["is_success"] is True

# Tests for auth_register
@pytest.mark.systemtest
def test_auth_register_http():
    """
        - HTTP test for auth_register
    """
    # Create a user
    data_dict = {
        "name_first": "test",
        "name_last": "testing",
        "email": "test@test.com",
        "password": "12345678"
    }
    response = requests.post(
        "http://127.0.0.1:8080/auth/register", json=data_dict)
    register_dict = response.json()

    # Get the list of users
    registered_token_dict = {"token": register_dict["token"]}
    response1 = requests.get(
        "http://127.0.0.1:8080/users/all", params=registered_token_dict)
    list_of_users = response1.json()

    assert len(list_of_users) == 1
