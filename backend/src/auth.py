"""
 - Code for auth.py in T18B - Blue Project
"""
import re
import smtplib
import ssl
import jwt
from jwt.exceptions import DecodeError
import abstractions
from error import InputError

# pylint: disable = C0301

# Secret for encoding tokens
SECRET = 'Blue'
RESET_SECRET = 'BluePW'


# Checks if email input is valid
def email_check(email):
    """
        - Function, which gets called when you need to validate an inputed email
    """
    regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"

    valid_email = False
    if re.search(regex, email):
        valid_email = True

    return valid_email


def auth_login(email, password):
    """
        - Function, which authorises the login for a user
        - returns the users token and user_id
    """
    all_user_ids = abstractions.get_all_user_ids()
    # Check if email entered is valid
    if email_check(email) is False:
        raise InputError(description="Please input a valid email address")

    email_registered = False
    # Check if email matches with a registered user
    for user_id in all_user_ids:
        user = abstractions.get_user(user_id)
        if user['email'] == email:
            email_registered = True
            break

    if email_registered is False:
        # Doesnt match with any registered email
        raise InputError(
            description="Email entered has not been registered. Please register email and try again.")

    # Check if password matches
    if user is None:
        raise InputError(description="No registered user")

    if user['password'] != password:
        # Password doesn't match with user
        raise InputError(description="Incorrect Password. Please try again")

    # All details match, obtain token.
    token = jwt.encode({'u_id': user['user_id']},
                       SECRET, algorithm='HS256').decode('utf-8')

    # Mark user as logged in
    user['logged_in'] = True
    abstractions.update_user(user['user_id'], user)

    return {
        'token': token,
        'u_id': user["user_id"]
    }


def auth_logout(token):
    """
        - Function, which logs out a user when called.
    """
    is_success = False

    if check_valid_token(token) is True:
        user_id = get_user_from_token(token)
        user = abstractions.get_user(user_id)
        user['logged_in'] = False
        abstractions.update_user(user_id, user)
        is_success = True
    else:
        is_success = False

    return {
        "is_success": is_success,
    }


def auth_register(email, password, name_first, name_last):
    """
        - Function, which registers a user
        - Returns the users token and new user_id
    """
    # Check first name length
    if not 1 <= len(name_first) <= 50:
        raise InputError(
            description="First name entered is invalid. Please try again")

    # Check last name length
    if not 1 <= len(name_last) <= 50:
        raise InputError(
            description="Last name entered is invalid. Please try again")

    # Check if email entered is valid
    if email_check(email) is False:
        raise InputError(description="Please input a valid email address")

    # Check if email entered does not belong to another user
    all_user_ids = abstractions.get_all_user_ids()
    for user_id in all_user_ids:
        user = abstractions.get_user(user_id)
        if user['email'] == email:
            # Email has been registered
            raise InputError(
                description="An account with this email address already exists. Please login")

    # Check if the password is valid
    if len(password) < 6:
        raise InputError(
            description="Password is less then 6 characters. Please try again")

    # All tests passed create user
    user_id = abstractions.create_user(name_first, name_last, email, password)
    token = auth_login(email, password)

    user = abstractions.get_user(user_id)
    # If it is the first user created, give owner permissions
    if not all_user_ids:
        user['permission_level'] = 1

    user['handle'] = create_handle(name_first, name_last)
    # Update the user
    abstractions.update_user(user_id, user)

    return {
        'u_id': user_id,
        'token': token['token']
    }


def check_valid_token(token: str):
    """
        - Function, which checks if the given token is valid or not
    """
    valid_token = False
    user_id = get_user_from_token(token)
    user = abstractions.get_user(user_id)
    if user['logged_in'] is True:
        valid_token = True

    return valid_token


def get_user_from_token(token):
    """
        - Function, which returns the user_id for a specific user from there token
    """
    unzipped_dict = jwt.decode(token.encode(
        'utf-8'), SECRET, algorithms=['HS256'])
    user_id = unzipped_dict['u_id']

    return user_id


def create_handle(firstname, lastname, unique_int=None):
    """
        - Function, which creates a handle for a user
    """
    handle = f"{firstname.lower()}.{lastname.lower()}"
    # Check if the handle is too long
    if len(handle) > 20:
        # It is too long
        # Shorten it to only 20 characters
        handle = handle[:20]
    if unique_int is not None:
        handle += str(unique_int)
    if not check_unique_handle(handle):
        if unique_int is None:
            next_num = 1
        else:
            next_num = unique_int + 1
        return create_handle(firstname, lastname, next_num)
    return handle


def check_unique_handle(handle):
    """
        - Function, checks if the handle is unique and not used by anyone else in the program
    """
    all_user_ids = abstractions.get_all_user_ids()
    for user_id in all_user_ids:
        user = abstractions.get_user(user_id)
        if user['handle'] == handle:
            return False
    return True


def auth_password_reset_request(email):
    """
        - if the email given belongs to an account,
        it will send a code that would help reset the password
        - Code will be used in password_reset
    """
    # First check if email matches with a user
    all_user_ids = abstractions.get_all_user_ids()
    registered_email = False
    for user_id in all_user_ids:
        user = abstractions.get_user(user_id)
        if user['email'] == email:
            registered_email = True
            reset_code = jwt.encode({'u_id': user['user_id']},
                                    RESET_SECRET, algorithm='HS256').decode('utf-8')
            break

    # Code that will send the email
    if registered_email is True:
        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = "t18bblue@gmail.com"
        receiver_email = email
        password = "Blue4321"
        message = f"""\
        Slackr Password Reset Code
        

        The reset Code is: {reset_code}
        """
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

        # Set users code to true
        user['reset_code'] = True
        abstractions.update_user(user['user_id'], user)
    else:
        raise InputError(
            description="Emailed is not registered")

    return{}


def auth_password_reset(reset_code, new_password):
    """
        - If the reset code matches with another user
        - Change there password to the new password
    """
    # Check if new password is valid
    if len(new_password) < 6:
        raise InputError(
            description="Password is less then 6 characters. Please try again")

    # Unzip Token Dict and obtain user id
    try:
        reset_code_dict = jwt.decode(reset_code.encode(
            'utf-8'), RESET_SECRET, algorithms=['HS256'])
    except DecodeError:
        # If code is invalid raise an error
        raise InputError(
            description="Reset Code is invalid.")

    # Get user dictionary from u_id from token
    user_id = reset_code_dict["u_id"]
    user = abstractions.get_user(user_id)

    # if statement is to prevent another users code being used
    if user["reset_code"] is True:
        # Change password to new password
        # Set reset code to false to prevent it being used again for this user
        user["password"] = new_password
        user["reset_code"] = False
        # Update changes
        abstractions.update_user(user['user_id'], user)
    else:
        raise InputError(
            description="Reset Code is invalid")

    return{}
