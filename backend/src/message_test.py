'''
    Python program that includes all the test functions for message.py
'''
import datetime
import time
import requests
import pytest
import other
from error import InputError, AccessError
from message import message_send
from message import message_edit
from message import message_react
from message import message_unreact
from message import message_pin
from message import message_unpin
from message import message_remove
from channels import channels_create
from channel import channel_messages, channel_join, channel_addowner
from auth import auth_register

# INTEGRATION TESTS

# Function to wipe datafiles before each test
@pytest.fixture(autouse=True)
def wipe_datafiles():
    '''
    Delete all the data in the datafiles
    '''
    # Wipe before each run
    other.workplace_reset()
    yield
    # Wipe after each run
    other.workplace_reset()


@pytest.mark.integrationtest
def test_message_send_successful():
    '''
    Successful test case for message_send
    message_send takes in (token, channel_id, message) and outputs { message_id }
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')

    # acquire the channel_id
    # assuming channels_create works correctly
    channel_info = channels_create(user1['token'], 'new_channel', True)

    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)

    # check if the message id, user id and message content is correct
    assert message_data['messages'][0]['message'] == 'Hello World!'
    assert message_data['messages'][0]['message_id'] == message['message_id']
    assert message_data['messages'][0]['u_id'] == user1['u_id']


@pytest.mark.integrationtest
def test_message_send_2_messages_send_successful():
    '''
    Testing sending 2 messages using message_send
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)

    message1 = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message2 = message_send(
        user1['token'], channel_info['channel_id'], 'Goodbye World!')
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)

    # Reverse the messages
    message_data['messages'].reverse()

    # check if the message id, user id and message content is correct
    assert message_data['messages'][0]['message'] == 'Hello World!'
    assert message_data['messages'][0]['message_id'] == message1['message_id']
    assert message_data['messages'][0]['u_id'] == user1['u_id']
    # check if the second message exists
    assert message_data['messages'][1]['message'] == 'Goodbye World!'
    assert message_data['messages'][1]['message_id'] == message2['message_id']
    assert message_data['messages'][1]['u_id'] == user1['u_id']


@pytest.mark.integrationtest
def test_message_send_too_many_characters():
    '''
    Testing the error of sending a message with too many characters
    message_send takes in (token, channel_id, message) and outputs { message_id }
    '''
    user = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user['token'], 'new_channel', True)
    with pytest.raises(InputError):
        message_send(user['token'], channel_info['channel_id'], 'a' * 1001)


@pytest.mark.integrationtest
def test_message_send_access_error():
    '''
    Testing the failed case where user2 sends a message to
    the channel which he is not a member of
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    # a new authorised user that has not joined 'new_channel'
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    # AccessError when: the authorised user has not joined the channel they are trying to post to
    with pytest.raises(AccessError):
        message_send(user2['token'],
                     channel_info['channel_id'], 'Hello World!')


@pytest.mark.integrationtest
def test_message_remove_successful():
    '''
    Tesing removing a message in a channel
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    # create a message in the test channel
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    user2 = auth_register('z3261846@unsw.edu.au',
                          '323456789', 'LeBron', 'James')
    # assuming channel_addowner works correctly
    channel_join(user2['token'], channel_info['channel_id'])
    # remove this message
    message_remove(user1['token'], message['message_id'])
    message_data = channel_messages(
        user2['token'], channel_info['channel_id'], 0)
    # check if the list is now empty after the removal
    assert len(message_data['messages']) == 0


@pytest.mark.integrationtest
def test_message_remove_successful_other_owner():
    '''
    Testing another owner removing a message
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create a new user3 that is also a owner of this channel
    user3 = auth_register('z3261846@unsw.edu.au',
                          '323456789', 'LeBron', 'James')
    channel_join(user3['token'], channel_info['channel_id'])
    # assuming channel_addowner works correctly
    channel_addowner(user1['token'], channel_info['channel_id'], user3['u_id'])
    message_remove(user3['token'], message['message_id'])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)

    assert len(message_data['messages']) == 0


@pytest.mark.integrationtest
def test_message_remove_access_error_1():
    '''
    Testing message_remove with the user who is not an owner of the channel
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create user2 that is in the channel but is not an owner of the channel
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    channel_join(user2['token'], channel_info['channel_id'])

    with pytest.raises(AccessError):
        message_remove(user2['token'], message['message_id'])


@pytest.mark.integrationtest
def test_message_remove_access_error_2():
    '''
    Testing removing message executed by a user who is not in the channel
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create user2 that is not in the channel
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')

    with pytest.raises(AccessError):
        message_remove(user2['token'], message['message_id'])


@pytest.mark.integrationtest
def test_message_edit_successful():
    '''
    message_edit takes in (token, message_id, message) and outputs nothing
    Given a message, update it's text with new text
    If the new message is an empty string, the message is deleted
    '''
    user = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user['token'], 'new_channel', True)
    message = message_send(
        user['token'], channel_info['channel_id'], 'Hello World!')

    message_edit(user['token'], message['message_id'], 'HEY!')
    message_data = channel_messages(
        user['token'], channel_info['channel_id'], 0)

    # check if the message has been changed
    assert message_data['messages'][0]['message'] == 'HEY!'


@pytest.mark.integrationtest
def test_message_edit_successful_other_owner():
    '''
    Testing the successful case of editing a message
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create a new user3 that is also a owner of this channel
    user3 = auth_register('z3261846@unsw.edu.au',
                          '323456789', 'LeBron', 'James')
    channel_join(user3['token'], channel_info['channel_id'])
    # assuming channel_addowner works correctly
    channel_addowner(user1['token'], channel_info['channel_id'], user3["u_id"])
    message_edit(user3['token'], message['message_id'], 'Goodbye World!')
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)

    # check if the message has been changed
    assert message_data['messages'][0]['message'] == 'Goodbye World!'


@pytest.mark.integrationtest
def test_message_edit_access_error_1():
    '''
    Testing access error of the user (not an owner) editing other users' message
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create user2 that is in the channel but is not a owner of the channel
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    channel_join(user2['token'], channel_info['channel_id'])

    with pytest.raises(AccessError):
        message_edit(user2['token'], message['message_id'], 'Goodbye World!')


@pytest.mark.integrationtest
def test_message_edit_access_error_2():
    '''
    Testing the access error where the user who is not in the channel tries to edit the message.
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    # create user2 that is not in the channel
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')

    with pytest.raises(AccessError):
        message_edit(user2['token'], message['message_id'], 'Goodbye World!')


@pytest.mark.integrationtest
def test_message_react_successful():
    '''
    Testing message_react is successful
    '''
    react_id = 1
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_react(user1["token"], message["message_id"], react_id)
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["reacts"][0]["react_id"] == react_id
    assert message_data["messages"][0]["reacts"][0]["u_ids"][0] == user1["u_id"]

@pytest.mark.integrationtest
def test_message_react_invalid_react_id():
    '''
    Testing reacting to a message with an invalud react id
    '''
    react_id = 1000
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    with pytest.raises(InputError):
        message_react(user1["token"], message["message_id"], react_id)

@pytest.mark.integrationtest
def test_message_react_already_reacted():
    '''
    Testing reacting to a message that has already been reacted
    '''
    react_id = 1
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_react(user1["token"], message["message_id"], react_id)
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["reacts"][0]["react_id"] == react_id
    assert message_data["messages"][0]["reacts"][0]["u_ids"][0] == user1["u_id"]
    # this user has already reacted
    with pytest.raises(InputError):
        message_react(user1["token"], message["message_id"], react_id)


@pytest.mark.integrationtest
def test_message_unreact_successful():
    '''
    Testing successfully unreacting a message
    '''
    react_id = 1
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_react(user1["token"], message["message_id"], react_id)
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["reacts"][0]["react_id"] == react_id
    assert message_data["messages"][0]["reacts"][0]["u_ids"][0] == user1["u_id"]
    message_unreact(user1["token"], message["message_id"], react_id)
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["reacts"][0]["react_id"] == react_id
    assert len(message_data["messages"][0]["reacts"][0]["u_ids"]) == 0

@pytest.mark.integrationtest
def test_message_unreact_invalid_react_id():
    '''
    Testing unreacting a message with invalid react id
    '''
    react_id = 1
    invalid_react_id = 1000
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_react(user1["token"], message["message_id"], react_id)
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["reacts"][0]["react_id"] == react_id
    assert message_data["messages"][0]["reacts"][0]["u_ids"][0] == user1["u_id"]
    with pytest.raises(InputError):
        message_unreact(user1["token"], message["message_id"], invalid_react_id)


@pytest.mark.integrationtest
def test_message_pin_successful():
    '''
    Testing successfully pinning a message
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True


@pytest.mark.integrationtest
def test_message_pin_not_an_owner():
    '''
    Testing pinning the message by a user who is not an owner
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')

    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    channel_join(user2['token'], channel_info['channel_id'])
    # user2 is not the owner of the channel
    with pytest.raises(InputError):
        message_pin(user2["token"], message["message_id"])


@pytest.mark.integrationtest
def test_message_pin_already_pinned():
    '''
    Testing pinning the message that has already been pinned
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True

    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    channel_addowner(user1['token'], channel_info['channel_id'], user2['u_id'])
    with pytest.raises(InputError):
        message_pin(user2["token"], message["message_id"])


@pytest.mark.integrationtest
def test_message_pin_not_valid_message():
    '''
    Testing pinning the message that is not valid
    '''
    invalid_message_id = 1234567890
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    with pytest.raises(InputError):
        message_pin(user1["token"], invalid_message_id)


@pytest.mark.integrationtest
def test_message_unpin_successful():
    '''
    Testing successfully unpinning a message
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True
    message_unpin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["is_pinned"] is False


@pytest.mark.integrationtest
def test_message_unpin_not_an_owner():
    '''
    Testing unpinning a message by not an owner
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True
    user2 = auth_register('z4261846@unsw.edu.au',
                          '223456789', 'Hayden', 'Smith')
    channel_join(user2['token'], channel_info['channel_id'])
    # user2 is not the owner of the channel
    with pytest.raises(InputError):
        message_unpin(user2["token"], message["message_id"])


@pytest.mark.integrationtest
def test_message_unpin_not_valid_message():
    '''
    Testing unpinning a message that is not valid
    '''
    invalid_message_id = 1234567890
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True
    with pytest.raises(InputError):
        message_unpin(user1["token"], invalid_message_id)


@pytest.mark.integrationtest
def test_message_unpin_already_unpinned():
    '''
    Testing unpinning a message that has already been unpinned
    '''
    user1 = auth_register('z5261846@unsw.edu.au', '123456789', 'Yizhou', 'Cao')
    channel_info = channels_create(user1['token'], 'new_channel', True)
    message = message_send(
        user1['token'], channel_info['channel_id'], 'Hello World!')
    message_pin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data['messages'][0]['is_pinned'] is True
    message_unpin(user1["token"], message["message_id"])
    message_data = channel_messages(
        user1['token'], channel_info['channel_id'], 0)
    assert message_data["messages"][0]["is_pinned"] is False

    # message is already unpinned
    with pytest.raises(InputError):
        message_unpin(user1["token"], message["message_id"])

# SYSTEM TESTS


BASE_URL = "http://localhost:8080/"


def setup_test_user_http(email):
    '''
    Set up the required url of auth/register for the system tests
    '''
    data = {
        "email": email,
        "password": "ilovetrimesters",
        "name_first": "Hayden",
        "name_last": "Smith"
    }
    response = requests.post(BASE_URL + "auth/register", json=data)
    return response.json()


def setup_test_channel_http(token, public=True):
    '''
    Set up url of channels/create for the system tests
    '''
    data = {
        "token": token,
        "name": "Test Channel",
        "is_public": public
    }
    response = requests.post(BASE_URL + "channels/create", json=data)
    return response.json()


@pytest.mark.systemtest
def test_message_send_one_message_http():
    '''
    http testing for sending one message using message/send route
    '''
    message_content = "Hello World"
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["message"] == message_content


@pytest.mark.systemtest
def test_message_sendlater_http():
    '''
    http testing for sending one message 5 seconds later using message/sendlater route
    '''
    message_content = "Hello World"
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    now = datetime.datetime.now()
    message_later_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
        "time_sent": now.replace().timestamp() + 5
    }
    response = requests.post(
        BASE_URL + "message/sendlater", json=message_later_data)
    message_later_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert len(expected_messages["messages"]) == 0

    time.sleep(10)

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()
    assert len(expected_messages["messages"]) == 1


@pytest.mark.systemtest
def test_message_react_http():
    '''
    http testing for reacting one message using message/react route
    '''
    message_content = "Hello World"
    react_id = 1

    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    react_data = {
        "token": user_data["token"],
        "message_id": expected_messages["messages"][0]["message_id"],
        "react_id": react_id,
    }
    requests.post(BASE_URL + "message/react", json=react_data)

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["reacts"][0]["react_id"] == react_id
    assert expected_messages["messages"][0]["reacts"][0]["u_ids"][0] == user_data["u_id"]


@pytest.mark.systemtest
def test_message_unreact_http():
    '''
    http testing for unreacting one message using message/unreact route
    '''
    message_content = "Hello World"
    react_id = 1

    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    react_data = {
        "token": user_data["token"],
        "message_id": message_data['message_id'],
        "react_id": react_id,
    }
    requests.post(BASE_URL + "message/react", json=react_data)

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()
    assert expected_messages["messages"][0]["reacts"][0]["u_ids"][0] == user_data["u_id"]

    react_data = {
        "token": user_data["token"],
        "message_id": expected_messages["messages"][0]["message_id"],
        "react_id": react_id,
    }
    requests.post(BASE_URL + "message/unreact", json=react_data)

    # read the channel messages again
    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["reacts"][0]["react_id"] == react_id
    # check if the list is empty after removing the user from user_ids
    assert len(expected_messages["messages"][0]["reacts"][0]["u_ids"]) == 0


@pytest.mark.systemtest
def test_message_pin_http():
    '''
    http testing for pinning one message using message/pin route
    '''
    message_content = "Hello World"

    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    pin_data = {
        "token": user_data["token"],
        "message_id": expected_messages["messages"][0]["message_id"],
    }
    requests.post(BASE_URL + "message/pin", json=pin_data)

    # read the channel messages again
    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["is_pinned"] is True


@pytest.mark.systemtest
def test_message_unpin_http():
    '''
    http testing for unpinning one message using message/unpin route
    '''
    message_content = "Hello World"

    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    pin_data = {
        "token": user_data["token"],
        "message_id": expected_messages["messages"][0]["message_id"],
    }
    requests.post(BASE_URL + "message/unpin", json=pin_data)

    # read the channel messages again
    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["is_pinned"] is False


@pytest.mark.systemtest
def test_message_remove_http():
    '''
    http testing for removing one message using message/remove route
    '''
    message_content = "Hello World"
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["message"] == message_content

    remove_data = {
        "token": user_data["token"],
        "message_id": expected_messages["messages"][0]["message_id"],
    }
    response = requests.delete(BASE_URL + "message/remove", json=remove_data)
    assert len(expected_messages["messages"]) == 1
    # Get updated messages

    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()
    print(expected_messages["messages"])
    assert len(expected_messages["messages"]) == 0


@pytest.mark.systemtest
def test_message_edit_http():
    '''
    http testing for editing one message using message/edit route
    '''
    message_content = "Hello World"
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    message_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "message": message_content,
    }
    response = requests.post(BASE_URL + "message/send", json=message_data)
    message_data = response.json()

    messages_detail_params = {
        "token": user_data["token"],
        "channel_id": channel_data["channel_id"],
        "start": 0,
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["message"] == message_content

    new_message_content = "Goodbye World"
    edit_data = {
        "token": user_data['token'],
        "message_id": expected_messages["messages"][0]["message_id"],
        "message": new_message_content,
    }
    requests.put(BASE_URL + "message/edit", json=edit_data)
    # Get updated messages
    response = requests.get(BASE_URL + "channel/messages",
                            params=messages_detail_params)
    expected_messages = response.json()

    assert expected_messages["messages"][0]["message"] == new_message_content
