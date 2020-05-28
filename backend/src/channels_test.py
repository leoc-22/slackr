# pylint: disable = missing-docstring, line-too-long, redefined-outer-name
import pytest
import requests
from channels import channels_list, channels_listall, channels_create
from auth import auth_logout, auth_register
from error import InputError
import abstractions
import other
from channel import channel_join, channel_invite, channel_leave, channel_addowner, channel_removeowner

# this file contains the tests for all functions in channels.py


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

    result = auth_register(email, password, name_first, name_last)

    # store the token and u_id
    token = result['token']
    u_id = result['u_id']
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

    result = auth_register(email, password, name_first, name_last)

    # store the token and u_id
    token = result['token']
    u_id = result['u_id']
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
    # this fixture creates a new user using http request
    # only used for system tests
    data = {
        'email': "unswforever555@gmail.com",
        'password': "HappyPuppy101",
        'name_first': "unsw",
        'name_last': "lover",
    }
    # register a user with the details above
    response = requests.post(f"{BASE_URL}auth/register", json=data).json()

    # get the handle
    handle = abstractions.get_user(int(response['u_id']))['handle']

    user_detail = {
        'name_first': "unsw",
        'name_last': "lover",
        'u_id': response['u_id'],
        'email': "unswforever555@gmail.com",
        'token': response['token'],
        'handle': handle
    }
    return user_detail


@pytest.fixture
def user2_http():
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

    user2_detail = {
        'email': "hello12345678@gmail.com",
        'password': "2020Python1531",
        'name_first': "software",
        'name_last': "engineer",
        'token': response['token'],
        'u_id': response['u_id'],
        'handle': handle,
    }
    return user2_detail


def channel1_http(token: str, is_public: bool):
    # this function create a new channel
    # only used for channels system tests
    data = {
        'token': token,
        'name': "chan1",
        'is_public': is_public
    }
    # create a new channel with the details above
    response = requests.post(f"{BASE_URL}/channels/create", json=data).json()
    channel_id = response['channel_id']

    return {
        'channel_id': channel_id,
        'name': "chan1"
    }


def channel2_http(token: str, is_public: bool):
    # this function create a new channel
    # only used for channels system tests
    data = {
        'token': token,
        'name': "chan2",
        'is_public': is_public
    }
    # create a new channel with the details above
    response = requests.post(f"{BASE_URL}/channels/create", json=data).json()
    channel_id = response['channel_id']

    return {
        'channel_id': channel_id,
        'name': "chan2"
    }

################################################################################


@pytest.mark.systemtest
def test_channel_create_http(user1_http):

    # create a new channel by user1_http
    channel1 = channel1_http(user1_http['token'], True)
    assert channel1['channel_id'] == 1

# test with None as the input
# create_test1
@pytest.mark.integrationtest
def test_create_none_input():

    with pytest.raises(InputError):
        channels_create(None, "name", True)
        channels_create(None, "name", False)


# test if create() checks on the length of channel name
# create_test2
def test_create_very_long_name(user1):

    channel_name = "SuperLongNameeeeeeeeeeeee"

    with pytest.raises(InputError):
        channels_create(user1['token'], channel_name, True)
        channels_create(user1['token'], channel_name, False)

    auth_logout(user1['token'])


# test if create() raises InputError
# with a name of length == 20
# create_test3
@pytest.mark.integrationtest
def test_create_name_length_edge1(user1):

    channel_name = "SuperLongNameeeeeeee"

    result = channels_create(user1['token'], channel_name, True)
    assert result['channel_id'] == 1

    auth_logout(user1['token'])


# test with a channel name of length == 0
# create_test4
@pytest.mark.integrationtest
def test_create_name_length_edge2(user1):

    name = ''

    with pytest.raises(InputError):
        channels_create(user1['token'], name, True)
        channels_create(user1['token'], name, False)

    auth_logout(user1['token'])


#################################################################################


@pytest.mark.system
def test_channels_listall_http(user1_http, user2_http):

    # user1 creates a new channel
    channel1 = channel1_http(user1_http['token'], True)
    # user2 creates a new channel
    channel2 = channel2_http(user2_http['token'], True)

    data1 = {
        'token': user1_http['token']
    }
    lst1 = requests.get(f"{BASE_URL}channels/listall", params=data1).json()

    data2 = {
        'token': user2_http['token']
    }
    lst2 = requests.get(f"{BASE_URL}channels/listall", params=data2).json()

    assert lst1['channels'] == [
        {
            'channel_id': channel1['channel_id'],
            'name': "chan1",
        },
        {
            'channel_id': channel2['channel_id'],
            'name': "chan2"
        }
    ]

    assert lst2 == lst1


# test listall() when no channel created
# listall_test1
@pytest.mark.integrationtest
def test_listall_no_channel(user1):

    result = channels_listall(user1['token'])['channels']
    assert result == []

    auth_logout(user1['token'])


# test listall() with one created channel
# listall_test2
@pytest.mark.integrationtest
def test_listall_one_channel(user1):

    channels_create(user1['token'], "name", True)
    result = channels_listall(user1['token'])['channels']

    assert result == [{'channel_id': 1, 'name': "name"}]

    auth_logout(user1['token'])


# test on the 2 channels created by different users
# listall_test3
@pytest.mark.integrationtest
def test_listall_multiple_channels(user1, user2):

    # each user creates a channel
    channel1_id = channels_create(user1['token'], "name1", True)['channel_id']
    channel2_id = channels_create(user2['token'], "name2", True)['channel_id']

    result2 = channels_listall(user2['token'])['channels']
    result1 = channels_listall(user1['token'])['channels']

    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "name1",
        },
        {
            'channel_id': channel2_id,
            'name': "name2",
        }
    ]

    assert channel_lstall == result1
    assert result1 == result2

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_listall
# and if the list is changed if a user is invited to an existing channel
@pytest.mark.integrationtest
def test_channels_listall_invite(user1, user2):

    # create a new channel
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # get the list of all channels using user2 token
    lstall_before_invite = channels_listall(user2['token'])['channels']
    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lstall_before_invite == channel_lstall

    # user1 invites user2 to channel1
    channel_invite(user1['token'], channel1_id, user2['u_id'])

    # get the list of all channels again
    lstall_after_invite = channels_listall(user2['token'])['channels']
    # compare the lists
    assert lstall_before_invite == lstall_after_invite

    auth_logout(user1['token'])
    auth_logout(user2['token'])


###################################################################################


# list_test1, with no channel created
@pytest.mark.integrationtest
def test_list_no_channel(user1):

    result = channels_list(user1['token'])['channels']

    assert result == []

    auth_logout(user1['token'])


# test with one channel created
# list_test2
@pytest.mark.integrationtest
def test_list_one_channel(user1):

    channel_id = channels_create(user1['token'], "name", True)['channel_id']
    result = channels_list(user1['token'])['channels']

    channel_lst = [
        {
            'channel_id': channel_id,
            'name': "name"
        }
    ]

    assert result == channel_lst


# test with multiple channels created by multiple users
# list_test3
@pytest.mark.integrationtest
def test_list_multiple_channels(user1, user2):

    # each user creates a channel
    channel1_id = channels_create(user1['token'], "name1", True)['channel_id']
    channel2_id = channels_create(user2['token'], "name2", True)['channel_id']

    result2 = channels_list(user2['token'])['channels']
    result1 = channels_list(user1['token'])['channels']

    channel_lst1 = [
        {
            'channel_id': channel1_id,
            'name': "name1"
        }
    ]
    channel_lst2 = [
        {
            'channel_id': channel2_id,
            'name': "name2"
        }
    ]

    assert result1 == channel_lst1
    assert result2 == channel_lst2

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_listall
# and if the list is changed if a user joined to an existing channel
@pytest.mark.integrationtest
def test_channels_listall_join(user1, user2):

    # create a new channel, set it to be public so that user2 can join
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # get the list of all channels using user2 token
    lstall_before_join = channels_listall(user2['token'])['channels']
    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lstall_before_join == channel_lstall

    # user2 joins to channel1
    channel_join(user2['token'], channel1_id)

    # get the list of all channels again
    lstall_after_join = channels_listall(user2['token'])['channels']
    # compare the lists
    assert lstall_before_join == lstall_after_join

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_listall
# and if the list is changed if a user left an existing channel
@pytest.mark.integrationtest
def test_channels_listall_leave(user1, user2):

    # create a new channel, set it to be public so that user2 can join
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # user2 joins to channel1
    channel_join(user2['token'], channel1_id)

    # get the list of all channels using user2 token
    lstall_before_leave = channels_listall(user2['token'])['channels']
    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lstall_before_leave == channel_lstall

    # user2 leaves channel1
    channel_leave(user2['token'], channel1_id)

    # get the list of all channels again
    lstall_after_leave = channels_listall(user2['token'])['channels']
    # compare the lists
    assert lstall_before_leave == lstall_after_leave

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_listall
# and if the list is changed if a user is added as an owner to an existing channel
@pytest.mark.integrationtest
def test_channels_listall_addowner(user1, user2):

    # create a new channel by user1
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # get the list of all channels using user2 token
    lstall_before_addowner = channels_listall(user2['token'])['channels']
    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lstall_before_addowner == channel_lstall

    # user2 is added as an owner to channel1
    channel_addowner(user1['token'], channel1_id, user2['u_id'])

    # get the list of all channels again
    lstall_after_addowner = channels_listall(user2['token'])['channels']
    # compare the lists
    assert lstall_before_addowner == lstall_after_addowner

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_listall
# and if the list is changed if a user is removed as an owner to an existing channel
@pytest.mark.integrationtest
def test_channels_listall_removeowner(user1, user2):

    # create a new channel by user1
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # user2 is added as an owner to channel1
    channel_addowner(user1['token'], channel1_id, user2['u_id'])

    # get the list of all channels using user2 token
    lstall_before_removeowner = channels_listall(user2['token'])['channels']
    channel_lstall = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lstall_before_removeowner == channel_lstall

    # user1 removes user2
    channel_removeowner(user1['token'], channel1_id, user2['u_id'])

    # get the list of all channels again
    lstall_after_removeowner = channels_listall(user2['token'])['channels']
    # compare the lists
    assert lstall_before_removeowner == lstall_after_removeowner

    auth_logout(user1['token'])
    auth_logout(user2['token'])


###################################################################################
# this function tests on channels_list
# and if the list is changed if a user is invited to an existing channel
@pytest.mark.integrationtest
def test_channels_list_invite(user1, user2):

    # create a new channel
    channel1_id = channels_create(user1['token'], "chan1", False)['channel_id']

    # get the list ofchannels user2 is part of
    lst_before_invite = channels_list(user2['token'])['channels']
    assert lst_before_invite == []

    # user2 is invited to channel1
    channel_invite(user1['token'], channel1_id, user2['u_id'])

    channel_lst = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]

    # get the list of all channels user2 is part of again
    lst_after_invite = channels_list(user2['token'])['channels']
    # compare the lists
    assert lst_after_invite == channel_lst

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_list
# and if the list is changed if a user joins to an existing channel
@pytest.mark.integrationtest
def test_channels_list_join(user1, user2):

    # create a new channel
    channel1_id = channels_create(user1['token'], "chan1", True)['channel_id']

    # get the list ofchannels user2 is part of
    lst_before_join = channels_list(user2['token'])['channels']
    assert lst_before_join == []

    # user2 is invited to channel1
    channel_join(user2['token'], channel1_id)

    channel_lst = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]

    # get the list of all channels user2 is part of again
    lst_after_join = channels_list(user2['token'])['channels']
    # compare the lists
    assert lst_after_join == channel_lst

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_list
# and if the list is changed if a user is added as an owner to an existing channel
@pytest.mark.integrationtest
def test_channels_list_addowner(user1, user2):

    # create a new channel
    channel1_id = channels_create(user1['token'], "chan1", False)['channel_id']

    # get the list ofchannels user2 is part of
    lst_before_addowner = channels_list(user2['token'])['channels']
    assert lst_before_addowner == []

    # user2 is added as an owner to channel1
    channel_addowner(user1['token'], channel1_id, user2['u_id'])

    channel_lst = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]

    # get the list of all channels user2 is part of again
    lst_after_addowner = channels_list(user2['token'])['channels']
    # compare the lists
    assert lst_after_addowner == channel_lst

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_list
# and if the list is changed if a user left from an existing channel
@pytest.mark.integrationtest
def test_channels_list_leave(user1, user2):

    channel1_id = channels_create(user1['token'], "chan1", False)['channel_id']

    # invite user2 to channel1
    channel_invite(user1['token'], channel1_id, user2['u_id'])

    # get the list ofchannels user2 is part of
    lst_before_leave = channels_list(user2['token'])['channels']
    channel_lst = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lst_before_leave == channel_lst

    # user2 left channel1
    channel_leave(user2['token'], channel1_id)

    # get the list of all channels user2 is part of again
    lst_after_leave = channels_list(user2['token'])['channels']
    # compare the lists
    assert lst_after_leave == []

    auth_logout(user1['token'])
    auth_logout(user2['token'])


# this function tests on channels_list
# and if the list is changed if a user left from an existing channel
@pytest.mark.integrationtest
def test_channels_list_removeowner(user1, user2):

    channel1_id = channels_create(user1['token'], "chan1", False)['channel_id']

    # add user2 as an owner to channel1
    channel_addowner(user1['token'], channel1_id, user2['u_id'])

    # get the list ofchannels user2 is part of
    lst_before_removeowner = channels_list(user2['token'])['channels']
    channel_lst = [
        {
            'channel_id': channel1_id,
            'name': "chan1",
        }
    ]
    assert lst_before_removeowner == channel_lst

    # user2 is removed from channel1
    channel_removeowner(user1['token'], channel1_id, user2['u_id'])

    # get the list of all channels user2 is part of again
    lst_after_removeowner = channels_list(user2['token'])['channels']
    # compare the lists
    assert lst_after_removeowner == []

    auth_logout(user1['token'])
    auth_logout(user2['token'])


@pytest.mark.systemtest
def test_channels_list_http(user1_http, user2_http):

    # user1 creates a new channel
    channel1 = channel1_http(user1_http['token'], True)

    # user2 creates a new channel
    channel2 = channel2_http(user2_http['token'], False)

    data1 = {
        'token': user1_http['token']
    }
    lst1 = requests.get(f"{BASE_URL}/channels/list", params=data1).json()

    data2 = {
        'token': user2_http['token']
    }
    lst2 = requests.get(f"{BASE_URL}/channels/list", params=data2).json()

    assert lst1['channels'] == [
        {
            'channel_id': channel1['channel_id'],
            'name': "chan1"
        }
    ]
    assert lst2['channels'] == [
        {
            'channel_id': channel2['channel_id'],
            'name': "chan2"
        }
    ]
