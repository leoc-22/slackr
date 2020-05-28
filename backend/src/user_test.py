# pylint: disable = missing-docstring, redefined-outer-name
import pytest
import requests
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
from auth import auth_login, auth_logout, auth_register
from error import InputError
import abstractions
import other


# this file contains the tests for all functions in user.py


# Function to wipe datafiles before each test
@pytest.fixture(autouse=True)
def wipe_datafiles():
    # Wipe before each run
    other.workplace_reset()
    yield
    # Wipe after each run
    other.workplace_reset()


@pytest.fixture(autouse=False)
def user1():
    # this fixture create a new user
    # returns a dict containing registration details, login token and handle_str

    # register a user with following details:
    email = "hello12345678@gmail.com"
    password = "2020Python1531"
    name_first = "software"
    name_last = "engineer"

    auth_register(email, password, name_first, name_last)

    # login
    login_result = auth_login(email, password)
    token = login_result['token']
    u_id = login_result['u_id']
    handle = abstractions.get_user(u_id)['handle']

    detail = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'u_id': u_id,
        'token': token,
        'handle': handle,
    }
    return detail


@pytest.fixture(autouse=False)
def user2():
    # this fixture create a new user
    # returns a dict containing registration details, login token and handle_str

    # register another user with following details:
    # user2
    email = "unswforever555@gmail.com"
    password = "HappyPuppy101"
    name_first = "unsw"
    name_last = "lover"

    auth_register(email, password, name_first, name_last)

    # login and store the token and u_id
    login_result = auth_login(email, password)
    token = login_result['token']
    u_id = login_result['u_id']
    handle = abstractions.get_user(u_id)['handle']

    detail = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'u_id': u_id,
        'token': token,
        'handle': handle,
    }
    return detail


BASE_URL = 'http://127.0.0.1:8080/'


@pytest.fixture
def user1_http():
    # this function create user1
    # only used for http tests (system tests)
    # register a user with following details:
    data = {
        'email': "hello12345678@gmail.com",
        'password': "2020Python1531",
        'name_first': "software",
        'name_last': "engineer"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    response = response.json()

    # get the handle
    handle = abstractions.get_user(int(response['u_id']))['handle']

    user1_detail = {
        'email': "hello12345678@gmail.com",
        'password': "2020Python1531",
        'name_first': "software",
        'name_last': "engineer",
        'token': response['token'],
        'u_id': response['u_id'],
        'handle': handle,
    }
    return user1_detail


################################################################################


# test with an invalid u_id and valid token
# user_profile test1
@pytest.mark.integrationtest
def test_user_profile_invalid_u_id(user1):

    with pytest.raises(InputError):
        user_profile(user1['token'], -1)
        user_profile(user1['token'], None)

    auth_logout(user1['token'])


# test user_profile with valid u_id and token
# user_profile_test2
@pytest.mark.integrationtest
def test_user_profile_valid_u_id_token(user1):

    profile_result = user_profile(user1['token'], user1['u_id'])
    assert profile_result['email'] == user1['email']
    assert profile_result['name_first'] == user1['name_first']
    assert profile_result['name_last'] == user1['name_last']
    assert profile_result['u_id'] == user1['u_id']
    assert profile_result['handle_str'] == user1['handle']

    auth_logout(user1['token'])


#################################################################################

@pytest.mark.systemtest
def test_userprofile_http(user1_http):

    # create a user and get the token
    token = user1_http['token']
    u_id = user1_http['u_id']
    # get the user profile
    data = {
        'token': token,
        'u_id': u_id,
    }
    profile = requests.get(f"{BASE_URL}/user/profile", params=data).json()

    # compare the returned data with the input data used in register
    register_data = {
        'u_id': user1_http['u_id'],
        'email': user1_http['email'],
        'name_first': user1_http['name_first'],
        'name_last': user1_http['name_last'],
        'handle_str': user1_http['handle'],
        'profile_img_url': f'{BASE_URL}static/images/default.jpg',
    }
    assert profile == register_data


#################################################################################


# reset the first name into a name of length > 50
# user_profile_setname test1
@pytest.mark.integrationtest
def test_user_profile_setname_long_firstname(user1):

    # make a long first name of length > 50
    long_firstname = "softwareeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

    with pytest.raises(InputError):
        user_profile_setname(
            user1['token'], long_firstname, user1['name_last'])

    auth_logout(user1['token'])


# reset the first name into a name of length < 1
# user_profile_setname test2
@pytest.mark.integrationtest
def test_user_profile_setname_short_firstname(user1):

    with pytest.raises(InputError):
        user_profile_setname(user1['token'], "", user1['name_last'])
        user_profile_setname(user1['token'], None, user1['name_last'])

    auth_logout(user1['token'])


# reset the first name into a name of length == 50
# user_profile_setname test3
@pytest.mark.integrationtest
def test_user_profile_setname_firstname_length50(user1):

    # make a firstname of length == 50
    firstname_len_50 = "softwareeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

    user_profile_setname(user1['token'], firstname_len_50, user1['name_last'])

    # check if the first name is actually changed
    # and if others remain unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == firstname_len_50
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# test with first name of length == 1 (edge case
# test_user_profile_setname test4
@pytest.mark.integrationtest
def test_user_profile_setname_firstname_length1(user1):

    # make a new firstname and reset it
    new_firstname = "n"
    user_profile_setname(user1['token'], new_firstname, user1['name_last'])

    # check if the first name is actually changed
    # and if others remain unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == new_firstname
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# rest last name into a name of length > 50
# user_profile_setname test5
@pytest.mark.integrationtest
def test_user_profile_setname_long_lastname(user1):

    long_lastname = "engineerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"

    with pytest.raises(InputError):
        user_profile_setname(
            user1['token'], user1['name_first'], long_lastname)

    auth_logout(user1['token'])


# reset last name into a name of length < 1
# user_profile_setname test6
@pytest.mark.integrationtest
def test_user_profile_setname_short_lastname(user1):

    with pytest.raises(InputError):
        user_profile_setname(user1['token'], user1['name_first'], "")
        user_profile_setname(user1['token'], user1['name_first'], None)

    auth_logout(user1['token'])


# reset last name into a name of length == 50 (edge case
# user_profile_setname test7
@pytest.mark.integrationtest
def test_user_profile_setname_lastname_length50(user1):

    # make a last name of length == 50
    lastname_len_50 = "engineerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
    # reset
    user_profile_setname(user1['token'], user1['name_first'], lastname_len_50)

    # check if the last name is actually changed
    # and if others are unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == lastname_len_50
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset last name into a name of length == 1 (edge case
# user_profile_setname test8
@pytest.mark.integrationtest
def test_user_profile_setname_lastname_length1(user1):

    # make a last name of length == 1
    new_lastname = "n"
    # reset
    user_profile_setname(user1['token'], user1['name_first'], new_lastname)

    # check if the last name is actually changed
    # and if others are unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == new_lastname
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset both first and last name
# user_profile_setname test9
@pytest.mark.integrationtest
def test_user_profile_setname_both(user1):

    # make new names
    new_firstname = "hardware"
    new_lastname = "repairer"
    # reset
    user_profile_setname(user1['token'], new_firstname, new_lastname)

    # check if first and last name are actually changed
    # and if others remain unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == new_firstname
    assert user_detail['name_last'] == new_lastname
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset the first name into an invalid name
# reset last name into a valid name
# user_profile_setname test10
@pytest.mark.integrationtest
def test_user_profile_setname_do_nothing1(user1):

    # make new names
    long_firstname = "hardwareeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    good_lastname = "repairer"
    # reset
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], long_firstname, good_lastname)
        user_profile_setname(user1['token'], "", good_lastname)
        user_profile_setname(user1['token'], None, good_lastname)

    # check if all the user detail is unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset the last name into an invalid name
# reset first name into a valid name
# user_profile_setname test10
@pytest.mark.integrationtest
def test_user_profile_setname_do_nothing2(user1):

    # make new names
    good_firstname = "hardware"
    bad_lastname = "repairerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
    # reset
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], good_firstname, bad_lastname)
        user_profile_setname(user1['token'], good_firstname, "")
        user_profile_setname(user1['token'], good_firstname, None)

    # check if all the user detail is unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


@pytest.mark.systemtest
def test_userprofile_setname_http(user1_http):

    # the new names
    new_firstname = "youtube"
    new_lastname = "obsessor"

    # reset the firstname
    data = {
        'token': user1_http['token'],
        'name_first': new_firstname,
        'name_last': new_lastname
    }
    requests.put(f"{BASE_URL}/user/profile/setname", json=data)
    profile_data = {
        'u_id': user1_http['u_id'],
        'token': user1_http['token']
    }
    profile = requests.get(f"{BASE_URL}/user/profile",
                           params=profile_data).json()
    user1_detail = {
        'name_first': new_firstname,
        'name_last': new_lastname,
        'email': user1_http['email'],
        'handle_str': user1_http['handle'],
        'u_id': user1_http['u_id'],
        'profile_img_url': f'{BASE_URL}static/images/default.jpg',
    }
    assert user1_detail == profile

#################################################################################


# reset email into an invalid email address
# user_profile_setemail test1
@pytest.mark.integrationtest
def test_user_profile_setemail_invalid_email(user1):

    # make a bad email
    bad_email = "bv2pqy0w4[nb"

    # reset
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], bad_email)
        user_profile_setemail(user1['token'], "")
        user_profile_setemail(user1['token'], None)

    # check if all detail remains unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset the email into a used email
# user_profile_setemail test2
@pytest.mark.integrationtest
def test_user_profile_setemail_used_email(user1, user2):

    # reset user1's email into user2's email
    # reset user2's email into user1's email
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], user2['email'])
        user_profile_setemail(user2['token'], user1['email'])

    # check if user1 and user2 detail is unchanged
    user1_detail = user_profile(user1['token'], user1['u_id'])
    assert user1_detail['name_first'] == user1['name_first']
    assert user1_detail['name_last'] == user1['name_last']
    assert user1_detail['email'] == user1['email']
    assert user1_detail['u_id'] == user1['u_id']
    assert user1_detail['handle_str'] == user1['handle']

    user2_detail = user_profile(user2['token'], user2['u_id'])
    assert user2_detail['name_first'] == user2['name_first']
    assert user2_detail['name_last'] == user2['name_last']
    assert user2_detail['email'] == user2['email']
    assert user2_detail['u_id'] == user2['u_id']
    assert user2_detail['handle_str'] == user2['handle']

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# reset the email with a valid and unused email
# user_profile_setemail test3
@pytest.mark.integrationtest
def test_user_profile_setemail_valid_email(user1):

    # make a valid email
    good_email = "validemail345@gmail.com"

    # reset
    user_profile_setemail(user1['token'], good_email)

    # check if the email is changed
    # and others remain unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == good_email
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


@pytest.mark.systemtest
def test_userprofile_setemail(user1_http):

    new_email = "z123456@unsw.edu.au"
    data = {
        'token': user1_http['token'],
        'email': new_email,
    }
    # reset the email
    requests.put(f"{BASE_URL}/user/profile/setemail", json=data)

    # get updated detail
    profile_data = {
        'u_id': user1_http['u_id'],
        'token': user1_http['token'],
    }
    profile = requests.get(f"{BASE_URL}/user/profile",
                           params=profile_data).json()

    user1_detail = {
        'name_first': user1_http['name_first'],
        'name_last': user1_http['name_last'],
        'u_id': user1_http['u_id'],
        'email': new_email,
        'handle_str': user1_http['handle'],
        'profile_img_url': f'{BASE_URL}static/images/default.jpg',
    }
    assert user1_detail == profile

#################################################################################


# reset handle_str into a string whose length does not satisfy
## 3 <= length <= 20
@pytest.mark.integrationtest
def test_user_profile_sethandle_invalid(user1):

    # make invalid handle strings
    bad_handle1 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    bad_handle2 = "aa"

    # reset
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], bad_handle1)
        user_profile_sethandle(user1['token'], bad_handle2)
        user_profile_sethandle(user1['token'], None)
        user_profile_sethandle(user1['token'], "")

    # check if all detail remains unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == user1['handle']

    auth_logout(user1['token'])


# reset handle_str into a used string
# user_profile_sethandle test2
@pytest.mark.integrationtest
def test_user_profile_sethandle_used_handle(user1, user2):

    # reset user1's handle into user2's
    # reset user2's handle into user1's
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], user2['handle'])
        user_profile_sethandle(user2['token'], user1['handle'])

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# reset handle into a valid and unused handle
# user_profile_sethandle test3
@pytest.mark.integrationtest
def test_user_profile_sethandle_valid(user1):

    # make a valid handle
    good_handle = "hardwareengineer"

    # reset
    user_profile_sethandle(user1['token'], good_handle)

    # check if handle is changed successfully
    # and if other detail remain unchanged
    user_detail = user_profile(user1['token'], user1['u_id'])
    assert user_detail['name_first'] == user1['name_first']
    assert user_detail['name_last'] == user1['name_last']
    assert user_detail['email'] == user1['email']
    assert user_detail['u_id'] == user1['u_id']
    assert user_detail['handle_str'] == good_handle

    auth_logout(user1['token'])


@pytest.mark.systemtest
def test_userprofile_sethandle(user1_http):

    new_handle = 'aaaaaabbbc'
    data = {
        'token': user1_http['token'],
        'handle_str': new_handle
    }
    # reset the handle
    requests.put(f"{BASE_URL}/user/profile/sethandle", json=data)

    profile_data = {
        'token': user1_http['token'],
        'u_id': user1_http['u_id']
    }
    # get the updated details
    profile = requests.get(f"{BASE_URL}/user/profile",
                           params=profile_data).json()

    user1_detail = {
        'name_first': user1_http['name_first'],
        'name_last': user1_http['name_last'],
        'email': user1_http['email'],
        'handle_str': new_handle,
        'u_id': user1_http['u_id'],
        'profile_img_url': f'{BASE_URL}static/images/default.jpg',
    }
    assert user1_detail == profile
