'''
    Python program that has all functions about message of slackr
'''
import datetime
import abstractions
import auth
from error import AccessError, InputError

# pylint: disable=R1719


def message_send(token: str, channel_id: int, message: str):
    '''
    Send a message from authorised_user to the channel specified by channel_id

    Raises InputError when:
        message is more than 1000 characters
    Raises AccessError when:
        the authorised user has not joined the channel they are trying to post to
    '''
    # check if the token is valid
    if not auth.check_valid_token(token):
        raise AccessError(description="Invalid Token.")
    # check if the messaage string length exceeds 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters.")
    # Check for unsent messages
    check_unsent_messages()
    # get the authorised user"s id
    auth_user_id = auth.get_user_from_token(token)
    # get the channel detail (dictionary)
    channel_data = abstractions.get_channel(channel_id)
    # check if the authorised user is in the channel_data (dict)
    if auth_user_id not in channel_data["user_member_ids"]:
        raise AccessError(description="The user is not in the channel.")
    message_id = abstractions.create_message(auth_user_id, message, channel_id)
    # append the message id to channel["message_ids"] (list)
    channel_data["message_ids"].append(message_id)
    channel_data['message_count'] += 1
    # update this channel since new message is created
    abstractions.update_channel(channel_id, channel_data)
    return {
        "message_id": message_id
    }


def message_sendlater(token: str, channel_id: int, message: str, time_sent: int):
    '''
    Send a message from authorised_user to the channel specified by
    channel_id automatically at a specified time in the future

    Raises InputError when any of:
        Channel ID is not a valid channel
        Message is more than 1000 characters
        Time sent is a time in the past
    Raises AccessError when:
        the authorised user has not joined the channel they are trying to post to
    '''
    # check if the token is valid
    if not auth.check_valid_token(token):
        raise AccessError(description="Invalid Token.")
    # check if the messaage string length exceeds 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters.")
    # get the authorised user"s id
    auth_user_id = auth.get_user_from_token(token)
    # get the channel detail (dictionary)
    channel_data = abstractions.get_channel(channel_id)
    # check if the authorised user is in the channel_data (dict)
    if auth_user_id not in channel_data["user_member_ids"]:
        raise AccessError(description="The user is not in the channel.")
    message_id = abstractions.create_message(auth_user_id, message, channel_id)
    message_data = abstractions.get_message(message_id)
    message_data["time"] = datetime.datetime.fromtimestamp(time_sent)
    abstractions.create_unsent_message_id(message_id)
    abstractions.update_message(message_id, message_data)
    return {
        "message_id": message_id
    }


def message_react(token: str, message_id: int, react_id: int):
    '''
    Given a message within a channel the authorised user is part of,
    add a "react" to that particular message

    Raises InputError when any of:
        message_id is not a valid message within a channel that the authorised user has joined
        react_id is not a valid React ID.
        The only valid react ID the frontend has is 1
        Message with ID message_id already contains an active React
        with ID react_id from the authorised user
    '''
    auth_user_id = auth.get_user_from_token(token)
    message_data = abstractions.get_message(message_id)
    channel_data = abstractions.get_channel(message_data["channel_id"])
    if auth_user_id not in channel_data["user_member_ids"]:
        raise InputError(
            description="message_id is not a valid message")
    if react_id != 1:
        raise InputError(
            description="React_id is not a valid React ID.")
    for dictionary in message_data["reactions"]:
        if auth_user_id in dictionary["u_ids"]:
            raise InputError(
                description="Message already contains an active React")
    # assuming message_data["reactions"] = [{"react_id" : int, "u_ids" : []}, ]
    # check if in "reactions" the specified react_id has already existed
    dict_exist = False
    for dictionary in message_data["reactions"]:
        if dictionary["react_id"] == react_id:
            dictionary["u_ids"].append(auth_user_id)
            dict_exist = True
    # if there is no existing reaction dictionary in "reactions", create a new one
    if dict_exist is not True:
        new_reaction_data = {
            "react_id": auth_user_id,
            "u_ids": [auth_user_id],
        }
        message_data["reactions"].append(new_reaction_data)
    abstractions.update_message(message_id, message_data)

    return {}


def message_unreact(token: str, message_id: int, react_id: int):
    '''
    Given a message within a channel the authorised user is part of,
    remove a "react" to that particular message

    Raises InputError when:
        message_id is not a valid message
        within a channel that the authorised user has joined
        react_id is not a valid React ID
        Message with ID message_id does not contain an active React with ID react_id
    '''
    auth_user_id = auth.get_user_from_token(token)
    message_data = abstractions.get_message(message_id)
    channel_data = abstractions.get_channel(message_data["channel_id"])
    if auth_user_id not in channel_data["user_member_ids"]:
        raise InputError(
            description="message_id is not a valid message")
    if react_id != 1:
        raise InputError(
            description="React_id is not a valid React ID")
    for dictionary in message_data["reactions"]:
        if dictionary["react_id"] == react_id:
            if auth_user_id not in dictionary["u_ids"]:
                raise InputError(
                    description="Message does not contain an active React")
    for dictionary in message_data["reactions"]:
        if dictionary["react_id"] == react_id:
            dictionary["u_ids"].remove(auth_user_id)
    abstractions.update_message(message_id, message_data)

    return {}


def message_pin(token: str, message_id: int):
    '''
    Given a message within a channel,
    mark it as "pinned" to be given special display treatment by the frontend

    Raises InputError when any of:
        message_id is not a valid message
        Message with ID message_id is already pinned

    Raises AccessError when any of:
        The authorised user is not a member of the channel that the message is within
        The authorised user is not an owner
    '''
    auth_user_id = auth.get_user_from_token(token)
    user_data = abstractions.get_user(auth_user_id)
    if user_data["permission_level"] != 1:
        raise InputError(description="The authorised user is not an owner.")
    message_data = abstractions.get_message(message_id)
    if message_data is None:
        raise InputError(description="Message_id is not a valid message.")
    if message_data["pinned"] is True:
        raise InputError(description="Message is already pinned.")
    # get the channel_dict which contains the passed in message
    channel_data = abstractions.get_channel(message_data["channel_id"])
    # access error check
    if auth_user_id not in channel_data["user_member_ids"]:
        raise AccessError(
            description="User is not a member of the channel where the message is.")
    message_data["pinned"] = True
    abstractions.update_message(message_id, message_data)

    return {}


def message_unpin(token: str, message_id: int):
    '''
    Given a message within a channel, remove it's mark as unpinned

    InputError when any of:
        message_id is not a valid message
        Message with ID message_id is already unpinned

    AccessError when any of:
        The authorised user is not a member of the channel that the message is within
        The authorised user is not an owner
    '''
    auth_user_id = auth.get_user_from_token(token)
    user_data = abstractions.get_user(auth_user_id)
    if user_data["permission_level"] != 1:
        raise InputError(description="The authorised user is not an owner.")
    message_data = abstractions.get_message(message_id)
    if message_data is None:
        raise InputError(description="Message_id is not a valid message.")
    if message_data["pinned"] is False:
        raise InputError(description="Message is already unpinned.")
    # get the channel_dict which contains the passed in message
    channel_data = abstractions.get_channel(message_data["channel_id"])
    # access error check
    if auth_user_id not in channel_data["user_member_ids"]:
        raise AccessError(
            description="User is not a member of the channel that the message is within.")
    message_data["pinned"] = False
    abstractions.update_message(message_id, message_data)
    return {}


def message_remove(token: str, message_id: int):
    '''
    Given a message_id for a message,
    this message is removed from the channel

    InputError when any of:
        Message (based on ID) no longer exists

    AccessError when none of the following are true:
        Message with message_id was sent by the authorised user making this request
        The authorised user is an owner of this channel or the slackr
    '''
    auth_user_id = auth.get_user_from_token(token)
    user_data = abstractions.get_user(auth_user_id)
    # Access error check
    global_owner = True if user_data['permission_level'] == 1 else False
    message_data = abstractions.get_message(message_id)
    channel_data = abstractions.get_channel(message_data["channel_id"])
    channel_owner = True if auth_user_id in channel_data['owner_member_ids'] else False
    original_author = True if user_data['user_id'] == message_data["author_id"] else False
    if not (global_owner or channel_owner or original_author):
        raise AccessError(
            description="The authorised user is not the author of this message.")
    # Input error: if the message (base on message_id) no longer exists
    if abstractions.delete_message(message_id) is None:
        raise InputError(description="Message (based on ID) no longer exists.")
    channel_data['message_count'] -= 1
    channel_data['message_ids'].remove(message_id)
    abstractions.update_channel(channel_data['channel_id'], channel_data)
    return {}


def message_edit(token: str, message_id: int, message: str):
    '''
    Given a message, update it's text with new text.
    If the new message is an empty string, the message is deleted.

    AccessError when none of the following are true:
        Message with message_id was sent by the authorised user making this request
        The authorised user is an owner of this channel or the slackr
    '''
    # get the authorised user"s id
    auth_user_id = auth.get_user_from_token(token)
    user_data = abstractions.get_user(auth_user_id)
    # Access error check
    global_owner = True if user_data['permission_level'] == 1 else False
    message_data = abstractions.get_message(message_id)
    channel_data = abstractions.get_channel(message_data["channel_id"])
    channel_owner = True if auth_user_id in channel_data['owner_member_ids'] else False
    original_author = True if user_data['user_id'] == message_data["author_id"] else False
    if not (global_owner or channel_owner or original_author):
        raise AccessError(
            description="The authorised user is not the author of this message.")
    # replace the current message string in the message_data with the new message string
    message_data["content"] = message
    # update the boolean under "edited" key
    message_data["edited"] = True
    # update the message.json
    abstractions.update_message(message_id, message_data)
    return {}


def check_unsent_messages():
    '''
    Helper function to check unsent messages,
    used in message_sendlater function
    '''
    unsent_message_ids = abstractions.get_all_unsent_message_ids()
    for unsent_message_id in unsent_message_ids:
        # get the message
        message_data = abstractions.get_message(unsent_message_id)
        # check the datetime to see if it should have sent
        if message_data['time'] <= datetime.datetime.now():
            # The message should have sent
            send_unsent_message(unsent_message_id)


def send_unsent_message(message_id):
    '''
    Helper function to send unsent message,
    after checking there is unsent messages in the channel
    '''
    # This could be a standup message... check to remove standups
    mark_standups_as_completed()
    message_data = abstractions.get_message(message_id)
    # get channel
    channel_data = abstractions.get_channel(message_data['channel_id'])
    channel_data['message_ids'].append(message_id)
    channel_data['message_count'] += 1
    # remove id from queue
    abstractions.delete_unsent_message_id(message_id)
    # update channel
    abstractions.update_channel(message_data['channel_id'], channel_data)


def mark_standups_as_completed():
    '''
    Helper function to change boolean value when calling standup
    '''
    channel_ids = abstractions.get_all_channel_ids()
    now = datetime.datetime.now()
    for channel_id in channel_ids:
        channel_data = abstractions.get_channel(channel_id)
        if channel_data['standup_in_progress']:
            # Get the standup
            standup = abstractions.get_standup(channel_data['standup_id'])
            if standup['time_finished'] <= now:
                # This standup has finished
                standup['in_progress'] = False
                abstractions.update_standup(standup['standup_id'], standup)
                channel_data['standup_id'] = None
                channel_data['standup_in_progress'] = False
                abstractions.update_channel(channel_id, channel_data)
