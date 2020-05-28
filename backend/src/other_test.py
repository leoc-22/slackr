# pylint: disable = missing-docstring, redefined-outer-name
"""
 - other_test.py ~ T18B - Blue
 - Provides test cases for other.py
"""
import pytest
import requests
from error import AccessError, InputError
import other
import abstractions
import channel
import users
from auth import auth_register, auth_login
from channels import channels_create
from message import message_send


BASE_URL = "http://localhost:8080/"


# this url is used when running tests on vlab
# BASE_URL = 'http://127.0.0.1:5020/'
# BASE_URL1 = 'http://127.0.0.1:5020/'


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

###########################################################################


@pytest.fixture(autouse=False)
@pytest.mark.order(1)
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
@pytest.mark.order(2)
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


####################################################################


def setup_test_user():
    '''
    Assumptions:
        - User registration works
    '''
    register_results = auth_register(
        "test@test.com", "ilovetrimesters", "Hayden", "Jacobs")
    token = register_results['token']
    return token


@pytest.mark.integrationtest
def setup_test_channel(token, public=True):
    '''
    Assumptions:
        - Channel creation works
    '''
    creation_results = channels_create(token, "Hayden", public)
    channel_id = creation_results['channel_id']

    return channel_id


@pytest.mark.integrationtest
def test_users_all_one_user():
    '''
        - Test case for details of a user
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    user_dic = users.users_all(user1['token'])
    assert user_dic['users'][0]['u_id'] == user1['u_id']
    assert user_dic['users'][0]['email'] == 'z5261846@unsw.edu.au'
    assert user_dic['users'][0]['name_first'] == 'Yizhou'
    assert user_dic['users'][0]['name_last'] == 'Cao'
    assert user_dic['users'][0]['handle_str'] == 'yizhou.cao'


@pytest.mark.integrationtest
def test_users_all_multiple_user():
    '''
        - Test case for details of multiple users
    '''
    user1 = auth_register('z1261846@unsw.edu.au',
                          '123456789', 'LeBron', 'James')
    user2 = auth_register('z2261846@unsw.edu.au',
                          '223456789', 'James', 'Harden')
    user3 = auth_register('z3261846@unsw.edu.au',
                          '323456789', 'Kevin', 'Durant')
    user4 = auth_register('z4261846@unsw.edu.au',
                          '423456789', 'Kyrie', 'Irving')
    user5 = auth_register('z5261846@unsw.edu.au',
                          '523456789', 'Paul', 'George')
    user6 = auth_register('z6261846@unsw.edu.au',
                          '623456789', 'Kawhi', 'Leonard')

    user_id_list = [user1['u_id'], user2['u_id'], user3['u_id'],
                    user4['u_id'], user5['u_id'], user6['u_id']]
    user_dic = users.users_all(user1['token'])

    counter = 0
    for user in user_dic['users']:
        assert user['u_id'] == user_id_list[counter]
        counter += 1


@pytest.mark.integrationtest
def test_users_all_token():
    '''
        - Test case for users with tokens
    '''
    user1 = auth_register('z1261846@unsw.edu.au',
                          '123456789', 'LeBron', 'James')
    user2 = auth_register('z2261846@unsw.edu.au',
                          '223456789', 'James', 'Harden')
    user_dic_1 = users.users_all(user1['token'])
    user_dic_2 = users.users_all(user2['token'])

    # two users' token should output the same list of user detail.
    assert user_dic_1['users'] == user_dic_2['users']


@pytest.mark.integrationtest
def test_search_success_single_message_single_channel():
    '''
        - Search test for one message in one channel
    '''
    # Setup test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    channel.channel_join(user_token, channel_id)
    message = message_send(user_token, channel_id, "Hello World")

    # Test the search
    search_results = other.search(user_token, "Hello")
    assert len(search_results['messages']) == 1
    assert search_results['messages'][0]['message_id'] == message["message_id"]


@pytest.mark.integrationtest
def test_search_success_multiple_messages_single_channel():
    '''
        - Search test for multiple message in one channel
    '''
    # Setup test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    channel.channel_join(user_token, channel_id)
    message1 = message_send(user_token, channel_id, "Hello World")
    message2 = message_send(user_token, channel_id, "Hello there!")
    message_send(user_token, channel_id, "General Kenobi")

    # Search
    search_results = other.search(user_token, "Hello")

    # Verify results
    assert len(search_results['messages']) == 2
    matched_1 = False
    matched_2 = False
    for message in search_results['messages']:
        if message['message_id'] == message1['message_id']:
            matched_1 = True
        elif message['message_id'] == message2['message_id']:
            matched_2 = True
    assert matched_1 is True and matched_2 is True


@pytest.mark.integrationtest
def test_search_success_single_message_multiple_channels():
    '''
        - Search test for single message in multiple channels
    '''
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    channel2 = channels_create(user_token, "Smith", True)
    channel2_id = channel2['channel_id']

    # Join the channels
    channel.channel_join(user_token, channel_id)
    channel.channel_join(user_token, channel2_id)

    # Send the messages
    message1 = message_send(user_token, channel_id, "Hello world")
    message_send(user_token, channel2_id,
                 "A man has fallen into the river in lego city")

    # Search for 'Hello'
    search_results = other.search(user_token, "Hello")

    # Verify results
    assert len(search_results['messages']) == 1
    assert search_results['messages'][0]['message_id'] == message1["message_id"]


@pytest.mark.integrationtest
def test_search_success_multiple_messages_multiple_channels():
    '''
        - Search test for multiple messages in multiple channels
    '''
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    channel2 = channels_create(user_token, "Smith", True)
    channel2_id = channel2['channel_id']

    # Join the channels
    channel.channel_join(user_token, channel_id)
    channel.channel_join(user_token, channel2_id)

    # Send the messages
    message1 = message_send(user_token, channel_id, "Hello world")
    message2 = message_send(user_token, channel2_id,
                            "Hello from the other side")

    # Search for 'Hello'
    search_results = other.search(user_token, "Hello")

    # Verify results
    assert len(search_results['messages']) == 2
    matched_1 = False
    matched_2 = False
    for message in search_results['messages']:
        if message['message_id'] == message1['message_id']:
            matched_1 = True
        elif message['message_id'] == message2['message_id']:
            matched_2 = True
    assert matched_1 is True and matched_2 is True


@pytest.mark.integrationtest
def test_search_success_single_message_no_channel():
    '''
        Assumptions:
            - This will not cause an error, and will just return an empty list
    '''
    # Setup test user
    user_token = setup_test_user()

    # Search for 'Hello'
    search_results = other.search(user_token, "Hello")

    assert search_results['messages'] == []


@pytest.mark.integrationtest
def test_search_success_no_query_str():
    '''
        Assumptions:
            - This will return a list of every message
    '''
    # Setup test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    channel.channel_join(user_token, channel_id)

    # Send the message
    message_send(user_token, channel_id,
                 "The new emergency collection from LEGO City")

    # Search for nothing
    search_results = other.search(user_token, "")

    # Verify results
    assert len(search_results['messages']) == 1


# HTTP Tests
@pytest.mark.systemtest
def test_search_http():
    '''
        - HTTP test for search for single message in a single channel
    '''
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

    # Create a channel
    channel_create_dict = {
        "token": register_dict["token"],
        "name": "test_channel",
        "is_public": True
    }
    response1 = requests.post(
        "http://127.0.0.1:8080/channels/create", json=channel_create_dict)
    channel_dict = response1.json()

    # Send a message on the channel
    message_send_dict = {
        "token": register_dict["token"],
        "channel_id": channel_dict["channel_id"],
        "message": "test"
    }
    requests.post(
        "http://127.0.0.1:8080/message/send", json=message_send_dict)

    # Create a test query
    query_dict = {
        "token": register_dict["token"],
        "query_str": "test"
    }
    response3 = requests.get(
        "http://127.0.0.1:8080/search", params=query_dict)
    search_list = response3.json()
    assert len(search_list["messages"]) == 1


@pytest.mark.systemtest
def test_userpermissionchange_http():
    '''
    Tests to see if the user permission change works.
    Changes user2 to an owner.
    '''

    data = {
        "email": "test123@test.com",
        "password": "ilovetrimesters",
        "name_first": "Hayden",
        "name_last": "Smith"
    }
    response = requests.post(BASE_URL + "auth/register", json=data)
    user1_details = response.json()

    data2 = {
        "email": "second234@second.com",
        "password": "password",
        "name_first": "second",
        "name_last": "second"
    }
    response = requests.post(BASE_URL + "auth/register", json=data2)
    user2_details = response.json()

    userchangedata = {
        "token": user1_details["token"],
        "u_id": user2_details['u_id'],
        "permission_id": 1
    }
    response = requests.post(
        BASE_URL + "admin/userpermission/change", json=userchangedata)

    # check the user is marked as an owner
    user = abstractions.get_user(user2_details['u_id'])
    assert user['permission_level'] == 1


# test user_remove with invalid token
@pytest.mark.integrationtest
def test_removeuser_invalid_token():

    with pytest.raises(InputError):
        other.user_remove("", 1)
        other.user_remove(None, 1)
        other.user_remove("8418", 1)

# test user_remove with invalid user id


def test_removeuser_invalid_id(user1):

    # register a user
    token = user1['token']

    with pytest.raises(InputError):
        other.user_remove(token, -1)
        # since there is only one user
        other.user_remove(token, 100)


# test user_remove with lower permission level
@pytest.mark.integrationtest
def test_removeuser_unpermitted(user1, user2):

    # since user1 is the owner of the sleckr
    # user2 is not authorised to remove user1
    with pytest.raises(AccessError):
        other.user_remove(user2['token'], user1['u_id'])

    # check if user1 is removed
    users = abstractions.get_all_user_ids()
    assert user1['u_id'] in users


# test on successful removal
@pytest.mark.integrationtest
def test_removeuser_success(user1, user2):

    # user1 removes user2
    # as user1 is the first user
    other.user_remove(user1['token'], user2['u_id'])

    # check if user2 is removed
    users = abstractions.get_all_user_ids()
    assert not user2['u_id'] in users

# test on remove a removed user from a channel


def test_removeuser_chan(user1, user2):

    # user1 creates a new channel and invite user2 into it
    chan1 = channels_create(user1['token'], "chan1", True)
    channel.channel_invite(user1['token'], chan1['channel_id'], user2['u_id'])

    # user1 removes user2
    other.user_remove(user1['token'], user2['u_id'])

    # check if user2 is removed from chan1
    chan_dict = abstractions.get_channel(chan1['channel_id'])
    print(chan_dict, "-----------")
    assert not user2['u_id'] in chan_dict['user_member_ids']


@pytest.mark.systemtest
def test_removeuser_http(user1, user2):

    data = {
        'token': user1['token'],
        'u_id': int(user2['u_id'])
    }

    requests.delete(f"{BASE_URL}/admin/user/remove", json=data)

    # check if user2 is removed
    users = abstractions.get_all_user_ids()
    assert not user2['u_id'] in users
