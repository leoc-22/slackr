# pylint: disable = missing-docstring, redefined-outer-name
import pytest
import requests
import abstractions
from users import users_all
from auth import auth_logout, auth_register
from error import InputError
import other

BASE_URL = 'http://127.0.0.1:8080/'


@pytest.fixture(autouse=True)
def wipe_datafiles():
    # Wipe before each run
    other.workplace_reset()
    yield
    # Wipe after each run
    other.workplace_reset()


@pytest.fixture(autouse=False)
def user1():
    # register a user with following details:
    email = "hello12345678@gmail.com"
    password = "2020Python1531"
    name_first = "software"
    name_last = "engineer"

    result = auth_register(email, password, name_first, name_last)

    # store u_id and token
    token = result['token']
    u_id = result['u_id']
    handle = abstractions.get_user(u_id)['handle']

    detail = {
        'name_first': name_first,
        'name_last': name_last,
        'email': email,
        'password': password,
        'token': token,
        'u_id': u_id,
        'handle': handle,
    }
    return detail


@pytest.fixture
def user2():

    # register a user with following details:
    email = "hello87654321@gmail.com"
    password = "happyPython"
    name_first = "snow"
    name_last = "white"

    result = auth_register(email, password, name_first, name_last)

    # store u_id and token
    token = result['token']
    u_id = result['u_id']
    handle = abstractions.get_user(u_id)['handle']

    detail = {
        'name_first': name_first,
        'name_last': name_last,
        'email': email,
        'password': password,
        'token': token,
        'u_id': u_id,
        'handle': handle,
    }
    return detail


@pytest.fixture
def user3():

    # register a user with following details:
    email = "claphands378@gmail.com"
    password = "cherryBomb127"
    name_first = "BiggestHit"
    name_last = "OnTheStage"

    result = auth_register(email, password, name_first, name_last)

    # store u_id and token
    token = result['token']
    u_id = result['u_id']
    handle = abstractions.get_user(u_id)['handle']

    detail = {
        'name_first': name_first,
        'name_last': name_last,
        'email': email,
        'password': password,
        'token': token,
        'u_id': u_id,
        'handle': handle,
    }
    return detail


@pytest.fixture
def user1_http():
    data = {
        'email': "hello12345678@gmail.com",
        'password': "2020Python1531",
        'name_first':  "software",
        'name_last':  "engineer",
    }
    # register user1 with the detail above
    response = requests.post(f"{BASE_URL}/auth/register", json=data).json()
    # get the handle
    handle = abstractions.get_user(int(response['u_id']))['handle']

    user1_detail = {
        'email': "hello12345678@gmail.com",
        'name_first': "software",
        'name_last': "engineer",
        'token': response['token'],
        'u_id': response['u_id'],
        'handle': handle,
    }
    return user1_detail


@pytest.fixture
def user2_http():
    data = {
        'email': "hello87654321@gmail.com",
        'password': "happyPython",
        'name_first':  "snow",
        'name_last': "white",
    }
    # register user1 with the detail above
    response = requests.post(f"{BASE_URL}/auth/register", json=data).json()
    # get the handle
    handle = abstractions.get_user(int(response['u_id']))['handle']

    user2_detail = {
        'email': "hello87654321@gmail.com",
        'name_first': "snow",
        'name_last': "white",
        'token': response['token'],
        'u_id': response['u_id'],
        'handle': handle,
    }
    return user2_detail


@pytest.fixture
def user3_http():
    data = {
        'email': "claphands378@gmail.com",
        'password':  "cherryBomb127",
        'name_first':  "BiggestHit",
        'name_last': "OnTheStage",
    }
    # register user1 with the detail above
    response = requests.post(f"{BASE_URL}/auth/register", json=data).json()
    # get the handle
    handle = abstractions.get_user(int(response['u_id']))['handle']

    user3_detail = {
        'email': "claphands378@gmail.com",
        'name_first': "BiggestHit",
        'name_last': "OnTheStage",
        'token': response['token'],
        'u_id': response['u_id'],
        'handle': handle,
    }
    return user3_detail


################################################################################


@pytest.mark.integrationtest
def test_users_all_1(user1):

    assert users_all(user1['token'])['users'] == [{
        'u_id': user1['u_id'],
        'email': user1['email'],
        'name_first': user1['name_first'],
        'name_last': user1['name_last'],
        'handle_str': user1['handle'],
        'profile_img_url': 'default.jpg',
    }]

    auth_logout(user1['token'])


@pytest.mark.integrationtest
def test_users_invalid_token(user1):

    with pytest.raises(InputError):
        users_all(None)
        users_all("bciwgbi")

    auth_logout(user1['token'])


@pytest.mark.integrationtest
def test_users_all_multiple(user1, user2, user3):

    user_lst = [
        {
            'u_id': user1['u_id'],
            'email': user1['email'],
            'name_first': user1['name_first'],
            'name_last': user1['name_last'],
            'handle_str': user1['handle'],
            'profile_img_url': 'default.jpg',
        },
        {
            'u_id': user2['u_id'],
            'email': user2['email'],
            'name_first': user2['name_first'],
            'name_last': user2['name_last'],
            'handle_str': user2['handle'],
            'profile_img_url': 'default.jpg',
        },
        {
            'u_id': user3['u_id'],
            'email': user3['email'],
            'name_first': user3['name_first'],
            'name_last': user3['name_last'],
            'handle_str': user3['handle'],
            'profile_img_url': 'default.jpg',
        },
    ]

    all_users1 = users_all(user1['token'])['users']
    all_users2 = users_all(user2['token'])['users']
    all_users3 = users_all(user3['token'])['users']
    assert all_users1 == user_lst
    assert all_users1 == all_users2
    assert all_users2 == all_users3

    auth_logout(user1['token'])
    auth_logout(user2['token'])
    auth_logout(user3['token'])


@pytest.mark.systemtest
def test_uers_all_http(user1_http, user2_http, user3_http):

    # get the list of all users using the tokens from 3 users
    data1 = {
        'token': user1_http['token']
    }
    lst1 = requests.get(f"{BASE_URL}users/all", params=data1).json()
    lst1 = lst1['users']

    data2 = {
        'token': user2_http['token']
    }
    lst2 = requests.get(f"{BASE_URL}users/all", params=data2).json()
    lst2 = lst2['users']

    data3 = {
        'token': user3_http['token']
    }
    lst3 = requests.get(f"{BASE_URL}users/all", params=data3).json()
    lst3 = lst3['users']

    assert lst1 == [
        {
            'name_first': user1_http['name_first'],
            'name_last': user1_http['name_last'],
            'email': user1_http['email'],
            'u_id': user1_http['u_id'],
            'handle_str': user1_http['handle'],
            'profile_img_url': f'{BASE_URL}static/images/default.jpg',
        },
        {
            'name_first': user2_http['name_first'],
            'name_last': user2_http['name_last'],
            'email': user2_http['email'],
            'u_id': user2_http['u_id'],
            'handle_str': user2_http['handle'],
            'profile_img_url': f'{BASE_URL}static/images/default.jpg',
        },
        {
            'name_first': user3_http['name_first'],
            'name_last': user3_http['name_last'],
            'email': user3_http['email'],
            'u_id': user3_http['u_id'],
            'handle_str': user3_http['handle'],
            'profile_img_url': f'{BASE_URL}static/images/default.jpg',
        }
    ]
    assert lst2 == lst1
    assert lst3 == lst2
