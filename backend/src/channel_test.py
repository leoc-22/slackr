'''
File containing integration and system tests
'''
import pytest
import requests
import channel
import message as message_file
from channels import channels_create
from auth import auth_register
from error import AccessError, InputError


# pylint: disable=C0116,C0200

BASE_URL = "http://localhost:8080/"


def setup_test_user():
    '''
    Assumptions:
        - User registration works
    '''
    register_results = auth_register(
        "test@test.com", "ilovetrimesters", "Hayden", "Jacobs")
    token = register_results['token']
    return token


def setup_test_channel(token, public=True):
    '''
    Assumptions:
        - Channel creation works
    '''
    creation_results = channels_create(token, "Hayden", public)
    channel_id = creation_results['channel_id']

    return channel_id


def setup_test_user_http(email):
    data = {
        "email": email,
        "password": "ilovetrimesters",
        "name_first": "Hayden",
        "name_last": "Smith"
    }
    response = requests.post(BASE_URL + "auth/register", json=data)
    return response.json()


def setup_test_channel_http(token, public=True):
    data = {
        "token": token,
        "name": "Test Channel",
        "is_public": public
    }
    response = requests.post(BASE_URL + "channels/create", json=data)
    return response.json()


# Function to wipe datafiles before each test
@pytest.fixture(autouse=True)
def wipe_datafiles():
    # Wipe before each run
    requests.post(BASE_URL + "workplace/reset")
    yield
    # Wipe after each run
    requests.post(BASE_URL + "workplace/reset")


@pytest.mark.integrationtest
def test_channel_invite_success():
    '''
    Assumptions:
        - User registration works
        - Channel join works
        - Channel details works
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a new user we will invite
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Invite the new user
    channel.channel_invite(user_token, channel_id,
                           invited_user_results['u_id'])

    # Check that the new user is now in the channel
    channel_details = channel.channel_details(user_token, channel_id)
    user_in_channel = False
    channel_members = channel_details['all_members']
    for member in channel_members:
        if member['u_id'] == invited_user_results['u_id']:
            # We have found a matching user to the one we invited... Invitation success
            user_in_channel = True

    assert user_in_channel is True


@pytest.mark.integrationtest
def test_channel_invite_failure_1():
    '''
    Assumptions:
        - User registration works
    Expectations:
        - Will fail due to the user trying to invite not yet being in the channel.
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user to do the inviting
    second_user_results = auth_register(
        "test3@test3.com", "testytesty", "test", "testerson")

    # Create a new user we will invite
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    with pytest.raises(AccessError):
        # Invite the new user
        channel.channel_invite(second_user_results['token'], channel_id,
                               invited_user_results['u_id'])


@pytest.mark.integrationtest
def test_channel_invite_failure_2():
    '''
    Assumptions:
        - There is no user with u_id == -1

    Expectations:
        - Will fail as the user we are trying to invite does not exist.
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    with pytest.raises(InputError):
        # Invite the new user
        channel.channel_invite(user_token, channel_id, -1)


@pytest.mark.integrationtest
def test_channel_invite_failure_3():
    '''
    Assumptions:
        - There is no channel with channel_id == -1

    Expectations:
        - Will fail due to an input error being raised as the channel id we are trying is not valid.
    '''
    # Create test data
    user_token = setup_test_user()

    # Create a new user we will invite
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    with pytest.raises(InputError):
        channel.channel_invite(user_token, -1, invited_user_results['u_id'])


@pytest.mark.integrationtest
def test_channel_join_success():
    '''
    Assumptions:
        - User registration works
        - Channel details works
    '''
    # Create test data
    # Create a user to create the channel as user will already be in channel
    creator_user_token = setup_test_user()
    channel_id = setup_test_channel(creator_user_token)
    # Create second user to join the channel
    second_user = auth_register(
        "second@second.com", "password", "second", "test")
    user_token = second_user['token']

    # Join the user to the channel
    channel.channel_join(user_token, channel_id)

    # Get channel data
    channel_data = channel.channel_details(user_token, channel_id)

    # Search through the channel data and see if the user has been added
    user_in_channel = False
    all_members = channel_data['all_members']
    for member in all_members:
        if member['u_id'] == second_user['u_id']:
            user_in_channel = True

    assert user_in_channel is True


@pytest.mark.integrationtest
def test_channel_join_failure_1():
    '''
    Assumptions:
        - There is no channel with channel id == -1

    Expectations:
        - Will fail as the channel id is not valid
    '''

    # Create test data
    user_token = setup_test_user()

    with pytest.raises(InputError):
        # Try to add the user to a non-existent channel
        channel.channel_join(user_token, -1)


@pytest.mark.integrationtest
def test_channel_join_failure_2():
    '''
    Expectations:
        - Will fail as the channel is set to private
    '''

    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token, False)

    # Create another user who we will try and join the channel with
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    with pytest.raises(AccessError):
        # Try to add the user to a channel that is set to private
        channel.channel_join(invited_user_results['token'], channel_id)


@pytest.mark.integrationtest
def test_channel_details_success():
    '''
    Assumptions:
        - The person who created a channel is automatically an owner of that channel

    Expectations:
        - Will pass as the token and channel_id will be valid
    '''

    # Create test data
    register_results = auth_register(
        "test@test.com", "ilovetrimesters", "Hayden", "Jacobs")
    user_token = register_results['token']
    channel_id = setup_test_channel(user_token)

    channel_details = channel.channel_details(user_token, channel_id)

    expected_result = {
        "name": f"Hayden",
        "owner_members": [
            {
                "u_id": register_results['u_id'],
                "name_first": "Hayden",
                "name_last": "Jacobs",
                "profile_img_url": "default.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": register_results['u_id'],
                "name_first": "Hayden",
                "name_last": "Jacobs",
                "profile_img_url": "default.jpg",
            }
        ]
    }

    assert channel_details == expected_result


@pytest.mark.integrationtest
def test_channel_details_failure_1():
    '''
    Assumptions:
        - There is no channel with channel_id == -1

    Expectations:
        - Will fail as the channel id is not a valid channel
    '''
    # Create test data
    user_token = setup_test_user()

    with pytest.raises(InputError):
        channel.channel_details(user_token, -1)


@pytest.mark.integrationtest
def test_channel_details_failure_2():
    '''
    Assumptions:
        -

    Expectations:
        - Will fail as the authorised user is not a member of the channel
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user
    second_user = auth_register(
        "second@second.com", "password", "second", "second")
    with pytest.raises(AccessError):
        # Try and get the channel details without being in the channel
        channel.channel_details(second_user['token'], channel_id)


@pytest.mark.integrationtest
def test_channel_messages_success_single():
    '''
    Assumptions:
        - auth_register works
    Expectations:
        - Will succeed
    '''
    # Create test data
    register_results = auth_register(
        "test@test.com", "ilovetrimesters", "Hayden", "Jacobs")
    user_token = register_results['token']
    u_id = register_results['u_id']
    channel_id = setup_test_channel(user_token)

    # Send a test message to the test channel
    message_file.message_send(user_token, channel_id, "Hello world")

    # Get the channel messages
    message_data = channel.channel_messages(user_token, channel_id, 0)

    # Verify the pagination is working
    assert message_data['start'] == 0
    assert message_data['end'] == -1

    # Verify the first message in the channel we sent is working
    messages = message_data['messages']
    first_message = messages[0]
    assert first_message['message_id'] == 1
    assert first_message['u_id'] == u_id
    assert first_message['message'] == "Hello world"


@pytest.mark.integrationtest
def test_channel_messages_success_multiple():
    '''
        Expectations:
            - Will succeed
    '''
    # Create test data
    register_results = auth_register(
        "test@test.com", "ilovetrimesters", "Hayden", "Jacobs")
    user_token = register_results['token']
    u_id = register_results['u_id']
    channel_id = setup_test_channel(user_token)

    # Keep track of all the messages we will send in the channel
    sent_message_list = []
    for number in range(1, 101):
        message_file.message_send(
            user_token, channel_id, f"Test message: {number}")
        sent_message_list.append({
            "message_id": number,
            "u_id": u_id,
            "message": f"Test message: {number}"
        })

    # Get the channel messages
    message_data = channel.channel_messages(user_token, channel_id, 50)

    # Verify the pagination is working
    assert message_data['start'] == 50
    assert message_data['end'] == 100

    # Verify all messages were sent and then retrieved correctly
    counter = 100
    for message in message_data['messages']:
        local_message = sent_message_list[counter - 1]
        assert local_message['message_id'] == message['message_id']
        assert local_message['u_id'] == message['u_id']
        assert local_message['message'] == message['message']
        counter -= 1


@pytest.mark.integrationtest
def test_channel_messages_failure_1():
    '''
        Assumptions:
            - There is no channel with channel_id == -1
        Expectations:
            - Will fail as the channel ID is not a valid channel
    '''
    # Create test data
    user_token = setup_test_user()

    with pytest.raises(InputError):
        channel.channel_messages(user_token, -1, 0)


@pytest.mark.integrationtest
def test_channel_messages_failure_2():
    '''
    Assumptions:

    Expectations:
        - Will fail as we are requesting too high of a page
        (The start is greater than the total number of channel messages)
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    with pytest.raises(InputError):
        channel.channel_messages(user_token, channel_id, 100)


@pytest.mark.integrationtest
def test_channel_messages_failure_3():
    '''
    Assumptions:

    Expectations:
        - Will fail as the user issuing the request is not a part of the channel
    '''

    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create another user who we will try and get the channel messages with
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    with pytest.raises(AccessError):
        channel.channel_messages(invited_user_results['token'], channel_id, 0)


@pytest.mark.integrationtest
def test_channel_leave_success():
    '''
    Assumptions:
        - channel_join works
        - channel_detail works
    Expectations:
        - Will succeed
    '''
    # Create test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a user we will add and remove
    invited_user_results = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Add the users to the test channel
    channel.channel_join(invited_user_results['token'], channel_id)

    # Remove the test user from the test channel
    channel.channel_leave(invited_user_results['token'], channel_id)

    # Verify that the channel does not have the new user in it.
    # AKA the channel only has 1 member in it, the person who created it.
    channel_details = channel.channel_details(user_token, channel_id)
    assert len(channel_details['all_members']) == 1


@pytest.mark.integrationtest
def test_channel_leave_failure_1():
    '''
    Assumptions:
        - There is no channel with channel_id == -1
    Expectations:
        - Will fail as the channel ID is not a valid channel
    '''
    # Set up the test user
    user_token = setup_test_user()

    with pytest.raises(InputError):
        channel.channel_leave(user_token, -1)


@pytest.mark.integrationtest
def test_channel_leave_failure_2():
    '''
    Assumptions:
        - The user is not automatically added to the channel upon channel creation
    Expectations:
        - Will fail as the user is not a member of the channel
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second test user
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    with pytest.raises(AccessError):
        channel.channel_leave(second_user['token'], channel_id)


@pytest.mark.integrationtest
def test_channel_addowner_success():
    '''
    Assumptions:
        - The user who created the channel is automatically an owner
        - The channel_details function works
    Expectations:
        - Will succeed
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Add the users to the channel
    channel.channel_join(second_user['token'], channel_id)

    # Add the second user as an owner
    channel.channel_addowner(user_token, channel_id, second_user['u_id'])

    # Check that the second user is now in the channel details as an owner
    channel_details = channel.channel_details(user_token, channel_id)
    matched = False
    for member in channel_details['owner_members']:
        if member['u_id'] == second_user['u_id']:
            matched = True
    assert matched is True


@pytest.mark.integrationtest
def test_channel_addowner_failure_1():
    '''
    Assumptions:
        - There is no channel with channel_id == -1
    Expectations:
        - Will fail as the channel ID is not a valid channel
    '''
    # Set up the test data
    user_token = setup_test_user()

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Try and add the user as an owner of the non existent channel
    with pytest.raises(InputError):
        channel.channel_addowner(user_token, -1, second_user['u_id'])


@pytest.mark.integrationtest
def test_channel_addowner_failure_2():
    '''
    Assumptions:

    Expectations:
        - Will fail as the user is already an owner of this channel
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Add the users to the channel
    channel.channel_join(second_user['token'], channel_id)

    # Add the second user as an owner of the channel.
    # No error should be caused here
    channel.channel_addowner(user_token, channel_id, second_user['u_id'])

    # Try and add the user as an owner again
    with pytest.raises(InputError):
        channel.channel_addowner(user_token, channel_id, second_user['u_id'])


@pytest.mark.integrationtest
def test_channel_addowner_failure_3():
    '''
    Assumptions:
        - Channel join works
    Expectations:
        - Will fail as the authorised user is not an owner of channel or slackr
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")
    third_user = auth_register(
        "test3@test3.com", "ireallydolovetrimesters", "Jack", "Jackson")

    # Add the users to the channel
    channel.channel_join(second_user['token'], channel_id)
    channel.channel_join(third_user['token'], channel_id)

    # Try and add the third user as an owner of the channel using the second user's auth token
    with pytest.raises(AccessError):
        channel.channel_addowner(
            second_user['token'], channel_id, third_user['u_id'])


@pytest.mark.integrationtest
def test_channel_removeowner_success():
    '''
    Assumptions:
        - The user who created the channel is automatically an owner
        - The channel_details function works
        - The channel_addowner function works
    Expectations:
        - Will succeed
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Add the users to the channel
    channel.channel_join(second_user['token'], channel_id)

    # Add the second user as an owner
    channel.channel_addowner(user_token, channel_id, second_user['u_id'])

    # Remove the second user as an owner
    channel.channel_removeowner(user_token, channel_id, second_user['u_id'])

    # Check that the second user is not in the channel details as an owner
    channel_details = channel.channel_details(user_token, channel_id)
    no_match = True
    for member in channel_details['owner_members']:
        if member['u_id'] == second_user['u_id']:
            no_match = False
    assert no_match is True


@pytest.mark.integrationtest
def test_channel_removeowner_failure_1():
    '''
    Assumptions:
        - There is no channel with channel_id == -1
    Expectations:
        - Will fail as the channel does not exist
    '''

    # Set up the test data
    user_token = setup_test_user()

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Try and remove the user as owner from the nonexistent channel
    with pytest.raises(InputError):
        channel.channel_removeowner(user_token, -1, second_user['u_id'])


@pytest.mark.integrationtest
def test_channel_removeowner_failure_2():
    '''
    Assumptions:
        - channel_join works.
    Expectations:
        - Will fail as the user we are removing as owner is not an owner of the channel
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)

    # Create a second user we will add and make the owner of the channel
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")

    # Join the users to the channel
    channel.channel_join(second_user['token'], channel_id)

    # Try and remove the user as owner from the  channel
    with pytest.raises(InputError):
        channel.channel_removeowner(
            user_token, channel_id, second_user['u_id'])


@pytest.mark.integrationtest
def test_channel_removeowner_failure_3():
    '''
    Assumptions:
        - channel_join works
        - channel_addowner works
    Expectations:
        - Will fail as the authorised user is not an owner of the slackr or the channel
    '''
    # Set up the test data
    user_token = setup_test_user()
    channel_id = setup_test_channel(user_token)
    second_user = auth_register(
        "test2@test2.com", "ireallylovetrimesters", "John", "Smith")
    third_user = auth_register(
        "test3@test3.com", "ireallydolovetrimesters", "Jack", "Jackson")

    # Add the users to the channel
    channel.channel_join(second_user['token'], channel_id)
    channel.channel_join(third_user['token'], channel_id)

    # Add the second user as an owner in the channel
    channel.channel_addowner(user_token, channel_id, second_user['u_id'])

    # Try and use the third user to remove the second user as an admin
    with pytest.raises(AccessError):
        channel.channel_removeowner(
            third_user['token'], channel_id, second_user['u_id'])


@pytest.mark.systemtest
def test_channel_invite_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Setup a user to invite
    second_user_data = setup_test_user_http("second@second.com")

    # Invite the second user to the channel
    invite_data = {
        "token": user_data["token"],
        "channel_id": channel_data['channel_id'],
        "u_id": second_user_data["u_id"]
    }
    requests.post(BASE_URL + "channel/invite", json=invite_data)

    # Verify the second user is now in the channel
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()
    matched = False
    for user in channel_details['all_members']:
        if user['u_id'] == second_user_data['u_id']:
            matched = True

    # Assert there has been a matched user
    assert matched is True


@pytest.mark.systemtest
def test_channel_details_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Get the channel data
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()
    expected_details = {
        "name": "Test Channel",
        "owner_members": [{
            "u_id": user_data['u_id'],
            "name_first": "Hayden",
            "name_last": "Smith",
            'profile_img_url': f'{BASE_URL}static/images/default.jpg',
        }],
        "all_members": [{
            "u_id": user_data['u_id'],
            "name_first": "Hayden",
            "name_last": "Smith",
            'profile_img_url': f'{BASE_URL}static/images/default.jpg',
        }]
    }
    assert channel_details == expected_details


@pytest.mark.systemtest
def test_channel_messages_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Send 2 messages to the channel
    messages = []
    for num in range(2):
        message_content = f"Message number {num + 1}"
        message_data = {
            "token": user_data['token'],
            "channel_id": channel_data['channel_id'],
            "message": message_content
        }
        response = requests.post(BASE_URL + "message/send", json=message_data)
        message_data = response.json()
        messages.append({
            "message_id": message_data['message_id'],
            "u_id": user_data['u_id'],
            "message": message_content
        })

    # Retrieve the messages
    channel_messages_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "start": 0
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=channel_messages_params)
    channel_messages = response.json()
    assert len(messages) == len(channel_messages['messages'])
    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1

    # Reverse the channel messages
    channel_messages['messages'].reverse()
    for index in range(len(messages)):
        channel_message = channel_messages['messages'][index]
        stored_message = messages[index]
        assert channel_message['message_id'] == stored_message['message_id']
        assert channel_message['u_id'] == stored_message['u_id']
        assert channel_message['message'] == stored_message['message']


@pytest.mark.systemtest
def test_channel_leave_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a second user
    second_user_data = setup_test_user_http("second@second.com")

    # Add the second user to the channel
    join_data = {
        "token": second_user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    requests.post(BASE_URL + "channel/join", json=join_data)

    # Remove the second user from the channel
    requests.post(BASE_URL + "channel/leave", json=join_data)

    # Get the channel details to verify the user is not in it
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()
    matched = False
    for user in channel_details['all_members']:
        if user['u_id'] == second_user_data['u_id']:
            matched = True

    assert matched is False


@pytest.mark.systemtest
def test_channel_join_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a second user
    second_user_data = setup_test_user_http("second@second.com")

    # Add the second user to the channel
    join_data = {
        "token": second_user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    requests.post(BASE_URL + "channel/join", json=join_data)
    # Get the channel details to verify the user is in it
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()
    matched = False
    for user in channel_details['all_members']:
        if user['u_id'] == second_user_data['u_id']:
            matched = True

    assert matched is True


@pytest.mark.systemtest
def test_channel_addowner_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a second user
    second_user_data = setup_test_user_http("second@second.com")

    # Add the second user to the channel
    join_data = {
        "token": second_user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    requests.post(BASE_URL + "channel/join", json=join_data)

    # Make the second user an owner of the channel
    addowner_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "u_id": second_user_data['u_id'],
    }
    requests.post(BASE_URL + "channel/addowner", json=addowner_data)

    # Verify the second user is now an owner of the channel
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()

    matched = False
    for owner in channel_details['owner_members']:
        if owner['u_id'] == second_user_data['u_id']:
            matched = True

    assert matched is True


@pytest.mark.systemtest
def test_channel_removeowner_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a second user
    second_user_data = setup_test_user_http("second@second.com")

    # Add the second user to the channel
    join_data = {
        "token": second_user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    requests.post(BASE_URL + "channel/join", json=join_data)

    # Make the second user an owner of the channel
    addowner_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "u_id": second_user_data['u_id'],
    }
    requests.post(BASE_URL + "channel/addowner", json=addowner_data)

    # Remove the second user as an owner of the channel
    requests.post(BASE_URL + "channel/removeowner", json=addowner_data)

    # Verify that the second user is not an owner of the channel
    channel_details_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
    }
    response = requests.get(BASE_URL + "channel/details",
                            params=channel_details_params)
    channel_details = response.json()

    matched = False
    for owner in channel_details['owner_members']:
        if owner['u_id'] == second_user_data['u_id']:
            matched = True

    assert matched is False
