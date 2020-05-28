'''
Module to do backend work with all channel requests
'''
import abstractions
import message as message_file
from auth import check_valid_token, get_user_from_token
from error import AccessError, InputError

# pylint: disable=C0116,C0200,R1719,C0301,R0914


def channel_invite(token: str, channel_id: int, u_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel_id is valid and the authorised user is a part of it.
    authed_user_id = get_user_from_token(token)
    # Get the channel and see if it exists
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    # Check if the user is a part of the channel
    if authed_user_id not in channel['user_member_ids']:
        raise AccessError(
            description="Authorised user is not part of this channel.")
    # Check if the user is a valid user.
    target_user = abstractions.get_user(u_id)
    if target_user is None:
        raise InputError(description="Target user does not exist.")

    # Add the users ID to the channels list of its members
    channel['user_member_ids'].append(int(u_id))

    # Update the channel in the persistence layer
    abstractions.update_channel(channel_id, channel)

    return {}


def channel_details(token: str, channel_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    # Check that the user is a part of the channel
    authed_user_id = get_user_from_token(token)
    if authed_user_id not in channel['user_member_ids']:
        raise AccessError(
            description="Authorised user is not part of this channel.")

    # Categorise the data
    output_user_members = []
    output_owner_members = []
    for user_member_id in channel['user_member_ids']:
        user = abstractions.get_user(user_member_id)
        user_dict = {
            "u_id": user_member_id,
            "name_first": user['firstname'],
            "name_last": user['lastname'],
            "profile_img_url": user['profile_pic_url'],
        }
        output_user_members.append(user_dict)
        if user_member_id in channel['owner_member_ids']:
            output_owner_members.append(user_dict)

    return {
        "name": channel['channel_name'],
        "owner_members": output_owner_members,
        "all_members": output_user_members
    }


def channel_messages(token: str, channel_id: int, start: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel_id is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist.")
    # Check that the start is a valid number for this channel
    start = int(start)
    if start > channel['message_count']:
        raise InputError(
            description="Attempting to get more messages than currently exist in this channel")
    # Check that the user is a part of the channel
    authed_user_id = get_user_from_token(token)
    if authed_user_id not in channel['user_member_ids']:
        raise AccessError(
            description="Authorised user is not part of this channel.")

    # Check if there are any unsent messages we need to send before the messages are collected
    message_file.check_unsent_messages()
    # Get updated channel list in case there are new messages
    channel = abstractions.get_channel(channel_id)

    # Get the messages
    message_list = []
    # Slice the message
    if channel['message_count'] < start + 50:
        not_enough = True
        finish_bound = channel['message_count'] + 1
    else:
        not_enough = False
        finish_bound = start + 50
    selected_message_ids = channel['message_ids'][start:finish_bound]

    # Reverse the message_list so the most recent message is first
    selected_message_ids.reverse()
    for message_id in selected_message_ids:
        message = abstractions.get_message(message_id)
        reactions = message["reactions"]
        for reaction in reactions:
            user_reacted = authed_user_id in reaction['u_ids']
            reaction.update({"is_this_user_reacted": user_reacted})
        message_dict = {
            "message_id": message_id,
            "u_id":  message['author_id'],
            "message": message['content'],
            "time_created": message["time"].replace().timestamp(),
            "reacts": reactions,
            "is_pinned": message["pinned"]
        }
        message_list.append(message_dict)

    if not_enough is True:
        end_to_return = -1
    else:
        end_to_return = finish_bound
    return {
        "messages": message_list,
        "start": start,
        "end": end_to_return
    }


def channel_leave(token: str, channel_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel ID is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    # Check that the user is a part of the channel
    authed_user_id = get_user_from_token(token)
    if authed_user_id not in channel['user_member_ids']:
        raise AccessError(
            description="Authorised user is not part of this channel.")

    # Remove the user from the channel
    channel['user_member_ids'].remove(authed_user_id)
    # Update the channel in the persistence layer
    abstractions.update_channel(channel_id, channel)

    return {}


def channel_join(token: str, channel_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel ID is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    # Check if the channel is private
    authed_user_id = get_user_from_token(token)
    if channel['private'] is True:
        # Check if the user is a global admin or a channel admin
        user = abstractions.get_user(authed_user_id)
        global_owner = True if user['permission_level'] == 1 else False
        channel_owner = True if authed_user_id in channel['owner_member_ids'] else False
        if not (global_owner or channel_owner):
            raise AccessError(
                description="User not authorised to view this channel.")

    # Add the user to the channel
    channel['user_member_ids'].append(authed_user_id)
    # Update the channel in the persistence layer
    abstractions.update_channel(channel_id, channel)
    return {}


def channel_addowner(token: str, channel_id: int, u_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel ID is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    # Check if the user is already an owner of the channel
    if u_id in channel['owner_member_ids']:
        raise InputError(
            description="The user is already an owner of this channel.")
    # Check that the authorised user has the permissions to add an owner
    authed_user_id = get_user_from_token(token)
    authed_user = abstractions.get_user(authed_user_id)
    global_owner = True if authed_user['permission_level'] == 1 else False
    channel_owner = True if authed_user_id in channel['owner_member_ids'] else False
    if not (global_owner or channel_owner):
        raise AccessError(
            description="Authorised user does not have permission to add an owner in this channel.")

    # Add the user as an owner of the channel
    channel['owner_member_ids'].append(u_id)
    # Update the channel in the persistence layer
    abstractions.update_channel(channel_id, channel)

    return {}


def channel_removeowner(token: str, channel_id: int, u_id: int):
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    # Check if the channel ID is valid
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    # Check if the user is not already an owner of the channel
    if u_id not in channel['owner_member_ids']:
        raise InputError(
            description="The user is not an owner of this channel.")
    # Check that the authorised user has the permissions to remove an owner
    authed_user_id = get_user_from_token(token)
    authed_user = abstractions.get_user(authed_user_id)
    global_owner = True if authed_user['permission_level'] == 1 else False
    channel_owner = True if authed_user_id in channel['owner_member_ids'] else False
    if not (global_owner or channel_owner):
        raise AccessError(
            description="Authorised user does not have permission to remove an owner in this channel."
        )

    # Remove the user as an owner of the channel
    channel['owner_member_ids'].remove(u_id)
    # Update the channel in the persistence layer
    abstractions.update_channel(channel_id, channel)

    return {}
