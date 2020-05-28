'''
Code to handle standups
'''
import datetime
import abstractions
from auth import check_valid_token, get_user_from_token
from error import InputError, AccessError


def standup_start(token: str, channel_id: int, length: int):
    '''
    Start a standup
    '''
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    # Check if there is an active standup in the channel
    if channel['standup_in_progress']:
        raise InputError(
            description="An active standup is currently running in this channel")

    # Create the standup
    authed_user_id = get_user_from_token(token)
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=length)
    finish_time = now + delta
    standup_id = abstractions.create_standup(
        now, finish_time, authed_user_id, channel_id)
    channel['standup_in_progress'] = True
    channel['standup_id'] = standup_id

    # Create the message that will be sent
    message_id = abstractions.create_message(
        authed_user_id, "", channel['channel_id'])
    message = abstractions.get_message(message_id)
    message['time'] = finish_time
    abstractions.update_message(message_id, message)
    # Update the standup so that it knows which message belongs to it
    standup = abstractions.get_standup(standup_id)
    standup['message_id'] = message_id
    abstractions.update_standup(standup_id, standup)

    # Queue the mesasge to be sent later
    abstractions.create_unsent_message_id(message_id)

    # Update the channel
    abstractions.update_channel(channel_id, channel)

    return {
        "time_finish": finish_time.replace().timestamp()
    }


def standup_active(token: str, channel_id: int):
    '''
    Check if a standup is currently active in this channel
    '''
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    if not channel['standup_in_progress']:
        time_finish = None
    else:
        standup = abstractions.get_standup(channel['standup_id'])
        time_finish = standup['time_finished'].replace().timestamp()

    return {
        "is_active": channel['standup_in_progress'],
        "time_finish": time_finish
    }


def standup_send(token: str, channel_id: int, message: str):
    '''
    Send a message to get buffered in the standup message
    '''
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    # Check the messagae lenghth
    if len(message) > 1000:
        raise InputError(
            description="Message is more than 1000 characters long")
    # Check if there is an active standup in the channel
    if not channel['standup_in_progress']:
        raise InputError(
            description="An active standup is not currently running in this channel")

    # Check if the user is in the channel
    authed_user_id = get_user_from_token(token)
    if authed_user_id not in channel['user_member_ids']:
        raise AccessError(
            description="You do not have permission to send a message to this channel")

    # Get the standup
    standup = abstractions.get_standup(channel['standup_id'])
    user = abstractions.get_user(authed_user_id)

    # Get the message for the standup
    message_dict = abstractions.get_message(standup['message_id'])

    message_dict['content'] += f"{user['handle']}:    {message}\n"

    # Update the message
    abstractions.update_message(standup['message_id'], message_dict)

    return {}
