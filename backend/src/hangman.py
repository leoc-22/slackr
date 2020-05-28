'''
Backend functionality for hangman
'''
from random_word import RandomWords
from random_words import RandomWords as alternateRandomWords
import abstractions
from auth import get_user_from_token, check_valid_token
from error import InputError, AccessError

# pylint: disable=W0703


def hangman_start(token: str, channel_id: int):
    '''
    Raises input error if the channel id is not a valid channel id
    Raises input error if there is already a hangman game in progress in that channel

    Raises access error if the user is not part of the given channel

    Returns a dictionary containing an array of guesses, an array of incorrect guesses,
    and the number of lives left
    '''
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    authed_user_id = get_user_from_token(token)
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    if authed_user_id not in channel["user_member_ids"]:
        raise AccessError(
            description="This user is not a member of this channel")
    if channel['hangman_id'] is not None:
        raise InputError(description="Hangman game already in progress")
    hangman_id = create_game(authed_user_id, channel_id)
    channel['hangman_id'] = hangman_id
    abstractions.update_channel(channel_id, channel)
    hangman_game = abstractions.get_hangman(hangman_id)
    return_dict = {
        "guesses": hangman_game['guesses'],
        "lives": hangman_game['lives'],
        "incorrect_guesses": hangman_game['incorrect_guesses'],
    }
    return return_dict


def hangman_active(token: str, channel_id: int):
    '''
    Raises input error if the channel id is not a valid channel id.
    '''
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    authed_user_id = get_user_from_token(token)
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    if authed_user_id not in channel["user_member_ids"]:
        raise AccessError(
            description="This user is not a member of this channel")
    in_progress = bool(channel['hangman_id'])
    return {
        "in_progress": in_progress
    }


def hangman_details(token: str, channel_id: int):
    '''
    Raises input error if the channel id is not a valid channel id
    Raises input error if there is not a hangman game in progress in that channel

    Raises access error if the user is not part of the given channel

    Returns a dictionary containing an array of guesses, an array of incorrect guesses,
    and the number of lives left
    '''
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    authed_user_id = get_user_from_token(token)
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    if authed_user_id not in channel["user_member_ids"]:
        raise AccessError(
            description="This user is not a member of this channel")
    if channel['hangman_id'] is None:
        raise InputError(description="There is no hangman game in progress")
    hangman = abstractions.get_hangman(channel['hangman_id'])
    # Check if the game has finished and if so update it
    if hangman['finished'] is True:
        channel['hangman_id'] = None
        abstractions.update_channel(channel_id, channel)
    return_dict = {
        "guesses": hangman['guesses'],
        "lives": hangman['lives'],
        "incorrect_guesses": hangman['incorrect_guesses'],
        "current_hangman_id": hangman['hangman_id']
    }
    return return_dict


def hangman_guess(token: str, channel_id: int, guess: str):
    '''
    Raises input error if the channel id is not a valid channel id
    Raises input error if the guess is more than 1 letter long
    Raises input error if there is not a hangman game in progress in that channel

    Raises access error if the user is not part of the given channel

    Returns a dictionary containing an array of guesses, an array of incorrect guesses,
    and the number of lives left

    Check if the game is finished and if the hangman_id is set back to None
    '''
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    authed_user_id = get_user_from_token(token)
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    if len(guess) > 1:
        raise InputError(description="The guess is more than 1 letter long.")
    if channel["hangman_id"] is None:
        raise InputError(
            description="There is not a hangman game in progress in this channel.")
    if authed_user_id not in channel["user_member_ids"]:
        raise AccessError(
            description="The user is not part of the given channel.")
    hangman = abstractions.get_hangman(channel['hangman_id'])
    hangman = make_guess(channel["hangman_id"], guess)
    guesses = hangman["guesses"]
    incorrect_guesses = hangman["incorrect_guesses"]
    lives = hangman["lives"]

    # check if the game is finished
    if hangman['finished'] is True:
        channel['hangman_id'] = None
        abstractions.update_channel(channel_id, channel)
    return {
        "guesses": guesses,
        "incorrect_guesses": incorrect_guesses,
        "lives": lives,
    }


def create_game(creator_id: int, channel_id: int):
    '''
    Create a game of hangman
    '''
    word = get_word()
    if isinstance(word, tuple):
        topic = word[1]
        word = word[0]
    else:
        topic = None
    hangman_id = abstractions.create_hangman(
        word, creator_id, channel_id, topic)
    return hangman_id


def get_word():
    '''
    Returns a random word for hangman
    '''
    rand_words = RandomWords()
    try:
        word = rand_words.get_random_word(hasDictionaryDef="true",
                                          minLength=3, maxLength=26)
    except Exception:
        # This module depends on an external api and is probably rate limited.
        # We need to get a word another way
        return alternate_get_word()
    return word


def alternate_get_word():
    '''
    Alternative method to get a random word.
    '''
    # This module has an inbuilt word list.
    rand_words = alternateRandomWords()
    return rand_words.random_word()


def make_guess(hangman_id: int, letter: str):
    '''
    Make a guess in a hangman game.
    '''
    hangman = abstractions.get_hangman(hangman_id)
    # Check that there are still lives left and the game is not finished
    if hangman['lives'] <= 0 or hangman['finished'] is True:
        return hangman
    # Check that the letter has not been guessed already
    if letter.lower() in hangman['incorrect_guesses']:
        # This letter has already been guessed.
        # No need to remove another life
        return hangman
    # Check if the letter is actually a match
    if letter.lower() in hangman['word']:
        # The letter is a match.
        # Check this letter has not been guessed
        if letter.lower() in hangman['guesses']:
            # Already been guessed. Exit
            return hangman
        # Replace all matching indexes in guesses array with the letter.
        for index in range(len(hangman['word'])):
            if hangman['word'][index].lower() == letter.lower():
                # This should be converted to a letter
                hangman['guesses'][index] = letter.lower()
    else:
        # The letter is not in the word
        # Add the letter to incorrectly guessed letter list
        hangman['incorrect_guesses'].append(letter.lower())
        hangman['lives'] -= 1
    # Check if the game is finished
    if None not in hangman['guesses'] or hangman['lives'] == 0:
        # The game has finished
        hangman['finished'] = True
    # Update hangman
    abstractions.update_hangman(hangman_id, hangman)
    return hangman


def hangman_answer(token: str, channel_id: int, current_hangman_id: int):
    '''
    Raises InputError if the channel_id does not exist.
    Raises InputError if the user is not in the channel.
    Raises AccessError if the lives of this game is not zero.

    Return a dictionary which contains the correct word if this game is lost
    '''
    authed_user_id = get_user_from_token(token)
    channel = abstractions.get_channel(channel_id)
    if channel is None:
        raise InputError(description="This channel does not exist")
    if authed_user_id not in channel["user_member_ids"]:
        raise AccessError(
            description="This user is not a member of this channel")

    hangman = abstractions.get_hangman(current_hangman_id)
    answer = hangman["word"]
    return {
        "answer": answer
    }
