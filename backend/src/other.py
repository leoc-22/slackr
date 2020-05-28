# pylint: disable = missing-docstring
"""
 - other.py ~ T18B - Blue
"""
import datetime
import abstractions
from auth import check_valid_token, get_user_from_token
from error import InputError, AccessError


def search(token: str, query_str: str):
    """
        - When a user searches for a specific message, this function will be called
    """
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    authed_user_id = get_user_from_token(token)

    # Find and store all channels the user is a part of.
    joined_channel_ids = []
    all_channel_ids = abstractions.get_all_channel_ids()
    for channel_id in all_channel_ids:
        channel = abstractions.get_channel(channel_id)
        if authed_user_id in channel['user_member_ids']:
            joined_channel_ids.append(channel_id)

    # Find and store all messages in these joinend channels
    # that contain the query_str
    matched_messages = []
    all_message_ids = abstractions.get_all_message_ids()
    for message_id in all_message_ids:
        message = abstractions.get_message(message_id)
        if query_str.lower() in message['content'].lower():
            message_dict = {
                "message_id": message_id,
                "u_id":  message['author_id'],
                "message": message['content'],
                "time_created": message["time"].replace(tzinfo=datetime.timezone.utc).timestamp(),
                "reacts": message["reactions"],
                "is_pinned": message["pinned"]
            }
            matched_messages.append(message_dict)

    return {
        "messages": matched_messages
    }


def workplace_reset():
    """
        - Resets all workplace related setups
    """
    abstractions.setup_channels_json()
    abstractions.setup_messages_json()
    abstractions.setup_users_json()
    abstractions.setup_standups_json()
    return {}


def userpermission_change(token: str, u_id: int, permission_id: int):
    """
        - Changes the permission of a user
    """
    # Check the tokens validity
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")

    # Check if u_id is a valid user
    target_user = abstractions.get_user(u_id)
    if target_user is None:
        raise InputError(description="This user does not exist.")
    valid_permissions = [1, 2]
    if int(permission_id) not in valid_permissions:
        raise InputError(description="Invalid permission id.")

    # Check the authed users permissions
    authed_user_id = get_user_from_token(token)
    authed_user = abstractions.get_user(authed_user_id)
    if authed_user['permission_level'] != 1:
        raise AccessError(
            description="Invalid permission to change another users permission level.")

    # Change the permission level
    target_user['permission_level'] = int(permission_id)

    # Save the user
    abstractions.update_user(u_id, target_user)
    return {}


def user_remove(token: str, u_id: int):

    # check the validity of u_id
    users = abstractions.get_all_user_ids()
    if not u_id in users:
        raise InputError(description="User Does Not Exist\nCannot Remove")

    # check the validity of token
    if token is None or token == "":
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # check the permission level of the user
    user = get_user_from_token(token)
    user_dict = abstractions.get_user(user)
    if not user_dict['permission_level'] == 1:
        raise AccessError(
            description="Unauthorised Action\nCannot Remove User")

    # remove the user from data
    abstractions.delete_user(u_id)

    owner_ids = []
    member_ids = []
    chan_data = {}
    # remove the user from the channels
    # of which the user was part of
    channels = abstractions.get_all_channel_ids()
    for chan_id in channels:
        chan_dict = abstractions.get_channel(chan_id)
        if u_id in chan_dict['owner_member_ids']:
            owner_ids = chan_dict['owner_member_ids']
            owner_ids.remove(u_id)
            member_ids = chan_dict['user_member_ids']
            member_ids.remove(u_id)
            # if now channel has no member or user
            # delete ther channel
            if chan_dict['user_member_ids'] == [] and owner_ids == []:
                abstractions.delete_channel(chan_id)
            # else update the channel with the new owner list
            else:
                chan_data = chan_dict
                chan_data['owner_member_ids'] = owner_ids
                abstractions.update_channel(chan_id, chan_data)

        elif u_id in chan_dict['user_member_ids']:
            member_ids = chan_dict['user_member_ids']
            member_ids.remove(u_id)
            # update the channel
            chan_data = chan_dict
            chan_data['user_member_ids'] = member_ids
            abstractions.update_channel(chan_id, chan_data)

    return {}


def create_img_url(base_url, filename):
    return f"{base_url}/static/images/{filename}"
