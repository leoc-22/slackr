# pylint: disable = missing-docstring, len-as-condition, bad-continuation
import abstractions
from error import InputError
from auth import check_valid_token, get_user_from_token


def channels_list(token: str):

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # get the list of all channel ids
    channel_ids = abstractions.get_all_channel_ids()

    channels = []

    # get the user id from token
    user_id = get_user_from_token(token)
    # look at all channels and
    # see if the user is in the channel
    for channel_id in channel_ids:
        channel_dict = abstractions.get_channel(channel_id)
        if user_id in channel_dict['owner_member_ids']:

            channels.append(
                {
                    'channel_id': channel_id,
                    'name': channel_dict['channel_name']
                }
            )
        elif user_id in channel_dict['user_member_ids']:

            channels.append(
                {
                    'channel_id': channel_id,
                    'name': channel_dict['channel_name']
                }
            )

    return {
        "channels": channels,
    }


def channels_listall(token: str):

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    channels = []

    # get all channel ids
    channel_ids = abstractions.get_all_channel_ids()

    # fetch the channels details one by one
    # add the channels one by one
    # get_channel returns channel name given the id
    for channel_id in channel_ids:
        channel_dict = abstractions.get_channel(channel_id)
        channels.append({
            'channel_id': int(channel_id),
            'name': channel_dict['channel_name'],
        })

    return {
        "channels": channels
    }


def channels_create(token: str, name: str, is_public: bool):

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # check the validity and length of name
    if name is None:
        raise InputError(description="Channel name must not be None")
    if len(name) > 20:
        raise InputError(
            description="Channel name must not exceed 20 characters")
    if len(name) == 0:
        raise InputError(
            description="Channel name must contain at least 1 character")

    # get the user_id from the input token
    # as this user will be the owner of the new channel
    owner_id = get_user_from_token(token)

    # now call create_channel to create a new channel
    channel_id = abstractions.create_channel(
        channel_name=name,
        private=not is_public,
        creator_id=int(owner_id)
    )

    return {'channel_id': channel_id}
