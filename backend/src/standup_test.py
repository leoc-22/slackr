'''
Integration and system tests for the standup functionality
'''
import datetime
import time
import pytest
import requests
import standup
import channel
import other
from channels import channels_create
from error import InputError, AccessError
from auth import auth_register

# pylint: disable=C0116

BASE_URL = 'http://localhost:8080/'


@pytest.hookimpl()
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integrationtest: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "systemtest: mark test as a system test"
    )


# Function to wipe datafiles before each test
@pytest.fixture(autouse=True)
def wipe_datafiles():
    # Wipe before each run
    other.workplace_reset()
    yield
    # Wipe after each run
    other.workplace_reset()


def setup_test_user():
    '''
    Assumptions:
        - User registration works
    '''
    register_results = auth_register(
        email="test@test.com", password="ilovetrimesters", name_first="Hayden", name_last="Smith")
    return register_results


def setup_test_channel(token, public=True):
    '''
    Assumptions:
        - Channel creation works
    '''
    creation_results = channels_create(token, "Hayden", public)
    return creation_results


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


@pytest.mark.integrationtest
def test_standup_start_success():
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a standup
    now = datetime.datetime.now().replace().timestamp()
    standup_data = standup.standup_start(
        user_data['token'], channel_data['channel_id'], 60)

    # Verify results
    expected_finish = now + 60
    assert int(expected_finish) == int(standup_data['time_finish'])


@pytest.mark.integrationtest
def test_standup_start_failure_1():
    '''
    Assumptions:
        - there is no channel with channel_id == -1
    Expectation:
        - Will fail as the channel id is not a valid channel
    '''
    # Create a test user
    user_data = setup_test_user()

    with pytest.raises(InputError):
        standup.standup_start(user_data['token'], -1, 60)


@pytest.mark.integrationtest
def test_standup_start_failure_2():
    '''
    Expectation:
        - Will fail as there is a standup in progress already
    '''
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a standup
    standup.standup_start(
        user_data['token'], channel_data['channel_id'], 60)

    # Create a second standup
    with pytest.raises(InputError):
        standup.standup_start(
            user_data['token'], channel_data['channel_id'], 60)


@pytest.mark.integrationtest
def test_standup_active_success_1():
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a standup
    standup_data = standup.standup_start(
        user_data['token'], channel_data['channel_id'], 60)

    # Call standup active
    standup_active_data = standup.standup_active(
        user_data['token'], channel_data['channel_id'])
    assert standup_active_data['is_active'] is True
    assert standup_active_data['time_finish'] == standup_data['time_finish']


@pytest.mark.integrationtest
def test_standup_active_success_2():
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Call standup active
    standup_active_data = standup.standup_active(
        user_data['token'], channel_data['channel_id'])
    assert standup_active_data['is_active'] is False
    assert standup_active_data['time_finish'] is None


@pytest.mark.integrationtest
def test_standup_active_failure_1():
    '''
    Assumptions:
        - There is no channel with channel_id == -1
    Expectations
        - Will fail as channel id does not exist
    '''
    # Create a test user
    user_data = setup_test_user()

    with pytest.raises(InputError):
        standup.standup_active(
            user_data['token'], -1)


@pytest.mark.integrationtest
def test_standup_send_success():
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a standup
    standup.standup_start(
        user_data['token'], channel_data['channel_id'], 2)

    # Send some messages through standup_send
    expected_message = ""
    for num in range(2):
        message = f"Test message number {num + 1}"
        standup.standup_send(user_data['token'],
                             channel_data['channel_id'], message)
        expected_message += f"hayden.smith:    {message}\n"

    # Verify that no messages have been sent to the channel yet
    channel_messages = channel.channel_messages(
        user_data['token'], channel_data['channel_id'], 0)
    assert len(channel_messages['messages']) == 0

    # Sleep
    time.sleep(2)

    # Verify that one message has been sent to the channel
    channel_messages = channel.channel_messages(
        user_data['token'], channel_data['channel_id'], 0)
    assert len(channel_messages['messages']) == 1
    assert channel_messages['messages'][0]['message'] == expected_message


@pytest.mark.integrationtest
def test_standup_send_failure_1():
    '''
    Assumptions:
        - there is no channel with channel_id == -1
    Expectation:
        - Will fail as the channel does not exist
    '''
    # Create a test user
    user_data = setup_test_user()

    with pytest.raises(InputError):
        standup.standup_send(
            user_data['token'], -1, "This is a test message that will not send")


@pytest.mark.integrationtest
def test_standup_send_failure_2():
    '''
    Expectation
        - Will fail as the message is longer than 1000 characters
    '''
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a standup
    standup.standup_start(
        user_data['token'], channel_data['channel_id'], 2)

    # Try and send the message
    very_long_message = "hi" * 501

    with pytest.raises(InputError):
        standup.standup_send(
            user_data['token'], channel_data['channel_id'], very_long_message)


@pytest.mark.integrationtest
def test_standup_send_failure_3():
    '''
    Expectation
        - Will fail as there is no standup running in the channel
    '''
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Try and send the message
    message = "Test message"
    with pytest.raises(InputError):
        standup.standup_send(
            user_data['token'], channel_data['channel_id'], message)


@pytest.mark.integrationtest
def test_standup_send_failure_4():
    '''
    Expectation:
        - will fail as the user is not in the channel
    '''
    # Create a test user
    user_data = setup_test_user()
    # Create a test channel
    channel_data = setup_test_channel(user_data['token'])

    # Create a second user
    second_user_data = auth_register(
        email="second@second.com", password="testytesty",
        name_first="secondtest", name_last="secondtest")

    # Start the standup
    standup.standup_start(
        user_data['token'], channel_data['channel_id'], 2)

    # Try and send the message
    with pytest.raises(AccessError):
        standup.standup_send(
            second_user_data['token'], channel_data['channel_id'], "test message")


@pytest.mark.systemtest
def test_standup_start_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a standup
    standup_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "length": 60
    }
    response = requests.post(BASE_URL + "standup/start", json=standup_data)
    standup_start_data = response.json()

    # Check if an active standup exists
    standup_active_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "standup/active",
                            params=standup_active_params)
    standup_active_data = response.json()

    assert standup_active_data['is_active'] is True
    assert int(standup_active_data['time_finish']) == int(
        standup_start_data['time_finish'])


@pytest.mark.systemtest
def test_standup_active_true_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a standup
    standup_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "length": 60
    }
    response = requests.post(BASE_URL + "standup/start", json=standup_data)
    response.json()

    # Check if an active standup exists
    standup_active_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "standup/active",
                            params=standup_active_params)
    standup_active_data = response.json()

    assert standup_active_data['is_active'] is True


@pytest.mark.systemtest
def test_standup_active_false_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Check if an active standup exists
    standup_active_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id']
    }
    response = requests.get(BASE_URL + "standup/active",
                            params=standup_active_params)
    standup_active_data = response.json()

    assert standup_active_data['is_active'] is False
    assert standup_active_data['time_finish'] is None


@pytest.mark.systemtest
def test_standup_send_http():
    # Create a user
    user_data = setup_test_user_http("test@test.com")
    # Create a channel
    channel_data = setup_test_channel_http(user_data['token'], True)

    # Create a standup
    standup_data = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "length": 10
    }
    response = requests.post(BASE_URL + "standup/start", json=standup_data)
    response.json()

    # Send some messages through standup_send
    expected_message = ""
    for num in range(2):
        message = f"Test message number {num + 1}"
        message_dict = {
            "token": user_data['token'],
            "channel_id": channel_data['channel_id'],
            "message": message
        }
        requests.post(BASE_URL + "standup/send", json=message_dict)
        expected_message += f"hayden.smith:    {message}\n"

    # Verify that no messages have been sent to the channel yet
    channel_messages_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "start": 0
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=channel_messages_params)
    channel_messages = response.json()
    assert len(channel_messages['messages']) == 0

    # Sleep
    time.sleep(15)

    # Verify that one message has been sent to the channel
    channel_messages_params = {
        "token": user_data['token'],
        "channel_id": channel_data['channel_id'],
        "start": 0
    }
    response = requests.get(BASE_URL + "channel/messages",
                            params=channel_messages_params)
    channel_messages = response.json()
    assert len(channel_messages['messages']) == 1
    assert channel_messages['messages'][0]['message'] == expected_message
