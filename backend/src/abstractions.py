'''
    This file contains abstractions for working with the JSON files.
'''
import json
import datetime
import os
from error import DataError


def get_path():
    '''
    Get the path of the file and return a complete filename
    '''
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'data')
    return filename


def get_file_directory(file_name):
    '''
    Return a file dirctory when the file name is passed in
    '''
    return os.path.join(get_path(), f"{file_name}.json")


def setup_channels_json():
    '''
    Sets up the channels json file to have the correct structure.
    Call this to reset/setup the channels.json file.
    '''
    channels_structure = {
        "latest_channel_id": 0,
        "channel_ids": [],
        "channels": []
    }
    with open(get_file_directory('channels'), 'w') as f:
        json.dump(channels_structure, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def setup_users_json():
    '''
    Sets up the users json file to have the correct structure.
    Call this to reset/setup the users.json file.
    '''
    users_structure = {
        "latest_user_id": 0,
        "user_ids": [],
        "users": []
    }
    with open(get_file_directory('users'), 'w') as f:
        json.dump(users_structure, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def setup_messages_json():
    '''
    Sets up the messages json file to have the correct structure.
    Call this to reset/setup the messages.json file.
    '''
    messages_structure = {
        "latest_message_id": 0,
        "message_ids": [],
        "messages": [],
        "unsent_message_ids": []
    }
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(messages_structure, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def setup_standups_json():
    '''
    Sets up the standups json file to have the correct structure.
    Call this to reset/setup the standups.json file.
    '''
    standups_structure = {
        "latest_standup_id": 0,
        "standup_ids": [],
        "standups": []
    }
    with open(get_file_directory('standups'), 'w') as f:
        json.dump(standups_structure, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def setup_hangman_json():
    '''
    Sets up the hangman json file to have the correct structure.
    Call this to reset/setup the hangman.json file.
    '''
    hangman_structure = {
        "latest_hangman_id": 0,
        "hangman_ids": [],
        "hangmen": []
    }
    with open(get_file_directory('hangman'), 'w') as f:
        json.dump(hangman_structure, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def create_channel(channel_name: str, private: bool, creator_id: int):
    '''
    Creates a channel with given channel_name, privacy status.
    The creator will be the user with u_id == creator_id.
    Returns the channel_id of the newly created channel.
    '''
    # Load the data
    with open(get_file_directory('channels'), 'r') as f:
        current_data = json.load(f)
    # Get the current maximum channel id
    latest_channel_id = current_data['latest_channel_id']
    # Get the new maximum channel id
    new_channel_id = latest_channel_id + 1
    # Create the channel dictionary
    channel_dict = {
        "channel_id": new_channel_id,
        "channel_name": str(channel_name),
        "private": private,
        "owner_member_ids": [int(creator_id)],
        "user_member_ids": [int(creator_id)],
        "message_count": 0,
        "standup_in_progress": False,
        "standup_id": None,
        "hangman_id": None,
        "message_ids": [],
    }
    # Increment the maximum channel id
    current_data['latest_channel_id'] = new_channel_id
    # Add the new channel ID to the list of channel_ids
    current_data['channel_ids'].append(new_channel_id)
    # Add the channel dictionary to the list of channels
    current_data['channels'].append(channel_dict)
    # Save the data
    with open(get_file_directory('channels'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))
    # Return the new channel_id
    return new_channel_id


def get_channel(channel_id: int):
    '''
    Gets a channel with given channel_id.
    Returns None if a matching channel is not found.
    '''
    # Load the data
    with open(get_file_directory('channels'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a channel exists with that id
    if int(channel_id) not in current_data['channel_ids']:
        return None
    for channel in current_data['channels']:
        if channel['channel_id'] == int(channel_id):
            return channel


def update_channel(channel_id: int, channel_data: dict):
    '''
    Updates a channel with given channel_id.
    This will replace all stored channel data for that channel.
    Returns None if the channel could not be updated.
    '''
    # Verify that the channel_id is not being updated.
    if int(channel_id) != channel_data["channel_id"]:
        raise DataError
        return
    # Load the data
    with open(get_file_directory('channels'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a channel exists with that id
    if int(channel_id) not in current_data['channel_ids']:
        return None

    # Iterate through the channels
    for channel_index in range(len(current_data['channels'])):
        # Check for a match
        if current_data['channels'][channel_index]['channel_id'] == channel_data['channel_id']:
            # Replace the current data with the new data
            current_data['channels'][channel_index] = channel_data
            break

    # Save the data
    with open(get_file_directory('channels'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def delete_channel(channel_id: int):
    '''
    Deletes a channel with given channel_id.
    Returns None if the channel was not found.
    '''
    # Load the data
    with open(get_file_directory('channels'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a channel exists with that id
    if int(channel_id) not in current_data['channel_ids']:
        return None

    # Typecast channel_id to be an int
    channel_id = int(channel_id)

    # Remove the channel_id from the list of channel ids
    channel_ids = current_data['channel_ids']
    channel_ids.remove(channel_id)
    # Iterate through the channels and find the channel
    for channel in current_data['channels']:
        # Check for a match
        if channel['channel_id'] == channel_id:
            # Remove the channel
            current_data['channels'].remove(channel)
            break
    # Save the data
    with open(get_file_directory('channels'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))
    return True


def create_user(firstname: str, lastname: str, email: str, password: str):
    '''
    Creates a user with given firstname, lastname, email and password.
    By default this user will not be logged in or have a handle.
    Returns the user_id of the newly created user.
    '''
    # Load the data
    with open(get_file_directory('users'), 'r') as f:
        current_data = json.load(f)
    # Get the current maximum user id
    latest_user_id = current_data['latest_user_id']
    # Get the new maximum user id
    new_user_id = latest_user_id + 1
    # Create the user dictionary
    user_dict = {
        "user_id": new_user_id,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "password": password,
        "handle": "",
        "logged_in": False,
        # TODO change this to a default profile picture once profile pictures are implemented
        "profile_pic_url": "default.jpg",
        "permission_level": 2,
        "reset_code": False,
    }
    # Increment the maximum user id
    current_data['latest_user_id'] = new_user_id
    # Add the new user ID to the list of user_ids
    current_data['user_ids'].append(new_user_id)
    # Add the user dictionary to the list of users
    current_data['users'].append(user_dict)
    # Save the data
    with open(get_file_directory('users'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))
    # Return the new user_id
    return new_user_id


def get_user(user_id: int):
    '''
    Gets a user with given user_id.
    Returns None if the user is not found.
    '''
    # Load the data
    with open(get_file_directory('users'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a user exists with that id
    if int(user_id) not in current_data['user_ids']:
        return None
    for user in current_data['users']:
        if user['user_id'] == int(user_id):
            return user


def update_user(user_id: int, user_data: dict):
    '''
    Updates a user with the given user_id.
    This will replace all stored user data for that user.
    Returns None if a matching user is not found.
    '''
    # Verify that the user_id is not being updated.
    if int(user_id) != user_data["user_id"]:
        raise DataError
        return
    # Load the data
    with open(get_file_directory('users'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a user exists with that id
    if int(user_id) not in current_data['user_ids']:
        return None

    # Iterate through the users
    for user_index in range(len(current_data['users'])):
        # Check for a match
        if current_data['users'][user_index]['user_id'] == user_data['user_id']:
            # Replace the current data with the new data
            current_data['users'][user_index] = user_data
            break

    # Save the data
    with open(get_file_directory('users'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))


def delete_user(user_id: int):
    '''
    Deletes a user with given user_id.
    Returns None if the user was not found.
    '''
    # Load the data
    with open(get_file_directory('users'), 'r') as f:
        current_data = json.load(f)
    # Check to see if a user exists with that id
    if int(user_id) not in current_data['user_ids']:
        return None

    # Typecast user_id to be an int
    user_id = int(user_id)

    # Remove the user_id from the list of user ids
    user_ids = current_data['user_ids']
    user_ids.remove(user_id)
    # Iterate through the users and find the user
    for user in current_data['users']:
        # Check for a match
        if user['user_id'] == user_id:
            # Remove the user
            current_data['users'].remove(user)
            break
    # Save the data
    with open(get_file_directory('users'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '))
    return True


def create_message(author_id: int, message_content: str, channel_id: int):
    '''
    Creates a message from user with matching u_id == author id with
    message content equal to message content and in channel with
    channel_id == channel_id.
    Returns the message_id of the newly created message.
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Get the current maximum message id
    latest_message_id = current_data['latest_message_id']
    # Get the new maximum message id
    new_message_id = latest_message_id + 1
    # Create the message dictionary
    message_dict = {
        "message_id": new_message_id,
        "author_id": int(author_id),
        "channel_id": int(channel_id),
        "content": message_content,
        "time": datetime.datetime.now(),
        "reactions": [],
        "pinned": False,
        "edited": False,
    }
    # Increment the maximum message id
    current_data['latest_message_id'] = new_message_id
    # Add the new message ID to the list of message_ids
    current_data['message_ids'].append(new_message_id)
    # Add the message dictionary to the list of messages
    current_data['messages'].append(message_dict)
    # Save the data
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    # Return the new message_id
    return new_message_id


def get_message(message_id: int):
    '''
    Gets a message with given message_id.
    Returns None if the message is not found.
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a message exists with that id
    if int(message_id) not in current_data['message_ids']:
        return None
    for message in current_data['messages']:
        if message['message_id'] == int(message_id):
            return message


def update_message(message_id: int, message_data: dict):
    '''
    Updates a message with the given message_id.
    This will replace all stored message data for that message.
    Returns None if a matching message is not found.
    '''
    # Verify that the message_id is not being updated.
    if int(message_id) != message_data["message_id"]:
        raise DataError
        return
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a message exists with that id
    if int(message_id) not in current_data['message_ids']:
        return None

    # Iterate through the messages
    for message_index in range(len(current_data['messages'])):
        # Check for a match
        if current_data['messages'][message_index]['message_id'] == message_data['message_id']:
            # Replace the current data with the new data
            current_data['messages'][message_index] = message_data
            break

    # Save the data
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)


def delete_message(message_id: int):
    '''
    Deletes a message with given message_id.
    Returns None if the message was not found.
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a message exists with that id
    if int(message_id) not in current_data['message_ids']:
        return None

    # Typecast message_id to be an int
    message_id = int(message_id)

    # Remove the message_id from the list of message ids
    message_ids = current_data['message_ids']
    message_ids.remove(message_id)
    # Iterate through the messages and find the message
    for message in current_data['messages']:
        # Check for a match
        if message['message_id'] == message_id:
            # Remove the message
            current_data['messages'].remove(message)
            break
    # Save the data
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    return True


def create_unsent_message_id(message_id: int):
    '''
    Create unsent message id
    Return True if successful, otherwise return None
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    if message_id in current_data['unsent_message_ids']:
        return None
    current_data['unsent_message_ids'].append(int(message_id))

    # Save the data
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    return True


def delete_unsent_message_id(message_id: int):
    '''
    Delete the unsent message id
    If successful return True, otherwise return None
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    if message_id not in current_data['unsent_message_ids']:
        return None
    current_data['unsent_message_ids'].remove(int(message_id))

    # Save the data
    with open(get_file_directory('messages'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    return True


def create_standup(start_time: datetime.datetime,
                   finish_time: datetime.datetime, creator_id: int, channel_id: int):
    '''
    Creates a standup ranging from start_time to finish_time
    created by a user with user_id == creator_id and in channel
    with channel_id == channel_id.
    Returns the standup_id of the newly created standup.
    '''
    # Load the data
    with open(get_file_directory('standups'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Get the current maximum standup id
    latest_standup_id = current_data['latest_standup_id']
    # Get the new maximum standup id
    new_standup_id = latest_standup_id + 1
    # Check if the standup is in progress
    now = datetime.datetime.now()
    if start_time <= now <= finish_time:
        in_progress = True
    else:
        in_progress = False
    # Create the standup dictionary
    standup_dict = {
        "standup_id": new_standup_id,
        "time_started": start_time,
        "time_finished": finish_time,
        "creator_id": int(creator_id),
        "channel_id": int(channel_id),
        "in_progress": in_progress,
        "message_id": None

    }
    # Increment the maximum standup id
    current_data['latest_standup_id'] = new_standup_id
    # Add the new standup ID to the list of standup_ids
    current_data['standup_ids'].append(new_standup_id)
    # Add the standup dictionary to the list of standups
    current_data['standups'].append(standup_dict)
    # Save the data
    with open(get_file_directory('standups'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    # Return the new standup_id
    return new_standup_id


def get_standup(standup_id: int):
    '''
    Gets a standup with the given standup_id.
    Returns None if a matching standup is not found.
    '''
    # Load the data
    with open(get_file_directory('standups'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a standup exists with that id
    if int(standup_id) not in current_data['standup_ids']:
        return None
    for standup in current_data['standups']:
        if standup['standup_id'] == int(standup_id):
            return standup


def update_standup(standup_id: int, standup_data: dict):
    '''
    Updates a standup with the given standup_id.
    This will replace all stored standup data for that standup.
    Returns None if a matching standup is not found.
    '''
    # Verify that the standup_id is not being updated.
    if int(standup_id) != standup_data["standup_id"]:
        raise DataError
        return
    # Load the data
    with open(get_file_directory('standups'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a standup exists with that id
    if int(standup_id) not in current_data['standup_ids']:
        return None

    # Iterate through the standups
    for standup_index in range(len(current_data['standups'])):
        # Check for a match
        if current_data['standups'][standup_index]['standup_id'] == standup_data['standup_id']:
            # Replace the current data with the new data
            current_data['standups'][standup_index] = standup_data
            break

    # Save the data
    with open(get_file_directory('standups'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)


def delete_standup(standup_id: int):
    '''
    Deletes a standup with given standup_id.
    Returns None if the standup was not found.
    '''
    # Load the data
    with open(get_file_directory('standups'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a standup exists with that id
    if int(standup_id) not in current_data['standup_ids']:
        return None

    # Typecast standup_id to be an int
    standup_id = int(standup_id)

    # Remove the standup_id from the list of standup ids
    standup_ids = current_data['standup_ids']
    standup_ids.remove(standup_id)
    # Iterate through the standups and find the standup
    for standup in current_data['standups']:
        # Check for a match
        if standup['standup_id'] == standup_id:
            # Remove the standup
            current_data['standups'].remove(standup)
            break
    # Save the data
    with open(get_file_directory('standups'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    return True


def create_hangman(word: str, creator_id: int, channel_id: int, topic: str = None):
    '''
    Creates a hangman game with a given word belonging to a certain topic.
    created by a user with user_id == creator_id and in channel
    with channel_id == channel_id.
    Returns the hangman_id of the newly created hangman.
    '''
    # Load the data
    with open(get_file_directory('hangman'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Get the current maximum hangman id
    latest_hangman_id = current_data['latest_hangman_id']
    # Get the new maximum hangman id
    new_hangman_id = latest_hangman_id + 1
    # Check if the hangman is in progress
    # Create the hangman dictionary
    hangman_dict = {
        "hangman_id": new_hangman_id,
        "topic": topic,
        "word": word,
        "guesses": [None if letter.isalpha() else letter for letter in word],
        "incorrect_guesses": [],
        "lives": 6,
        "creator_id": int(creator_id),
        "channel_id": int(channel_id),
        "finished": False,
    }
    # Increment the maximum hangman id
    current_data['latest_hangman_id'] = new_hangman_id
    # Add the new hangman ID to the list of hangman_ids
    current_data['hangman_ids'].append(new_hangman_id)
    # Add the hangman dictionary to the list of hangmans
    current_data['hangmen'].append(hangman_dict)
    # Save the data
    with open(get_file_directory('hangman'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    # Return the new hangman_id
    return new_hangman_id


def get_hangman(hangman_id: int):
    '''
    Gets a hangman with the given hangman_id.
    Returns None if a matching hangman is not found.
    '''
    # Load the data
    with open(get_file_directory('hangman'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a hangman exists with that id
    if int(hangman_id) not in current_data['hangman_ids']:
        return None
    for hangman in current_data['hangmen']:
        if hangman['hangman_id'] == int(hangman_id):
            return hangman


def update_hangman(hangman_id: int, hangman_data: dict):
    '''
    Updates a hangman with the given hangman_id.
    This will replace all stored hangman data for that hangman.
    Returns None if a matching hangman is not found.
    '''
    # Verify that the hangman_id is not being updated.
    if int(hangman_id) != hangman_data["hangman_id"]:
        raise DataError
        return
    # Load the data
    with open(get_file_directory('hangman'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a hangman exists with that id
    if int(hangman_id) not in current_data['hangman_ids']:
        return None

    # Iterate through the hangmans
    for hangman_index in range(len(current_data['hangmen'])):
        # Check for a match
        if current_data['hangmen'][hangman_index]['hangman_id'] == hangman_data['hangman_id']:
            # Replace the current data with the new data
            current_data['hangmen'][hangman_index] = hangman_data
            break

    # Save the data
    with open(get_file_directory('hangman'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)


def delete_hangman(hangman_id: int):
    '''
    Deletes a hangman with given hangman_id.
    Returns None if the hangman was not found.
    '''
    # Load the data
    with open(get_file_directory('hangman'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    # Check to see if a hangman exists with that id
    if int(hangman_id) not in current_data['hangman_ids']:
        return None

    # Typecast hangman_id to be an int
    hangman_id = int(hangman_id)

    # Remove the hangman_id from the list of hangman ids
    hangman_ids = current_data['hangman_ids']
    hangman_ids.remove(hangman_id)
    # Iterate through the hangmans and find the hangman
    for hangman in current_data['hangmen']:
        # Check for a match
        if hangman['hangman_id'] == hangman_id:
            # Remove the hangman
            current_data['hangmen'].remove(hangman)
            break
    # Save the data
    with open(get_file_directory('hangman'), 'w') as f:
        json.dump(current_data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), cls=DateTimeEncoder)
    return True


# Functions to get lists of all the data id's


def get_all_channel_ids():
    '''
    Get all channel ids into a list
    '''
    # Load the data
    with open(get_file_directory('channels'), 'r') as f:
        current_data = json.load(f)
    return current_data['channel_ids']


def get_all_user_ids():
    '''
    Get all user ids into a list
    '''
    # Load the data
    with open(get_file_directory('users'), 'r') as f:
        current_data = json.load(f)
    return current_data['user_ids']


def get_all_message_ids():
    '''
    Get all message ids into a list
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    return current_data['message_ids']


def get_all_standup_ids():
    '''
    Get all standup ids into a list
    '''
    # Load the data
    with open(get_file_directory('standups'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    return current_data['standup_ids']


def get_all_unsent_message_ids():
    '''
    Get all unsent message ids into a list
    '''
    # Load the data
    with open(get_file_directory('messages'), 'r') as f:
        current_data = json.load(f, object_hook=decode_datetime)
    return current_data['unsent_message_ids']


def get_all_hangman_ids():
    '''
    Get all hangman ids into a list
    '''
    # Load the data
    with open(get_file_directory('hangman'), 'r') as file:
        current_data = json.load(file, object_hook=decode_datetime)
    return current_data['hangman_ids']

# Encoders to help with converting datetimes


class DateTimeEncoder(json.JSONEncoder):
    '''
    Encoders to help with coverting datetimes
    '''
    def default(self, obj):                         # pylint: disable=E0202
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def decode_datetime(emp_dict):
    '''
    Serialize datetime into json
    '''
    # Credit: https://pynative.com/python-serialize-datetime-into-json/
    if 'time' in emp_dict:
        emp_dict['time'] = datetime.datetime.fromisoformat(emp_dict['time'])
    if 'time_started' in emp_dict:
        emp_dict['time_started'] = datetime.datetime.fromisoformat(
            emp_dict['time_started'])
    if 'time_finished' in emp_dict:
        emp_dict['time_finished'] = datetime.datetime.fromisoformat(
            emp_dict['time_finished'])
    return emp_dict
