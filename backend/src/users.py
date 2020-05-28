# pylint: disable = missing-docstring
import abstractions
from error import InputError
from auth import check_valid_token
from user import user_profile


def users_all(token: str):

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    users = []

    # get the list of all user ids
    user_ids = abstractions.get_all_user_ids()
    for user_id in user_ids:
        try:
            profile = user_profile(token, user_id)
            users.append(profile)

        except InputError:
            pass

    return {
        "users": users
    }
