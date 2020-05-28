# pylint: disable = anomalous-backslash-in-string, missing-docstring, len-as-condition, unused-import, too-many-locals, line-too-long, too-many-arguments
import shutil
import re
import os
from pathlib import Path
import requests
from PIL import Image
from flask import Flask, flash, request, redirect, url_for

import abstractions
from error import InputError
from auth import check_valid_token, get_user_from_token


def user_profile(token: str, u_id: int):

    # user_profile checks u_id and token respectively
    # and returns the user profiled given the user id
    # but does not check if the token aligns with the user_id

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # get the list of all users
    user_ids = abstractions.get_all_user_ids()
    # check if the u_id exists
    if u_id not in user_ids:
        raise InputError(description="User Not Exist")

    user_dict = abstractions.get_user(u_id)
    user = {
        'u_id': u_id,
        'email': user_dict['email'],
        'name_first': user_dict['firstname'],
        'name_last': user_dict['lastname'],
        'handle_str': user_dict['handle'],
        'profile_img_url': user_dict['profile_pic_url'],
    }

    return user


def user_profile_setname(token: str, name_first: str, name_last: str):
    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # check the length of first and last name
    if len(str(name_first)) < 1:
        raise InputError(
            description="'name_first' must contain at least 1 character")
    if len(str(name_first)) > 50:
        raise InputError(
            description="The length of 'name_first' must not exceed 50 characters")
    if len(str(name_last)) < 1:
        raise InputError(
            description="'name_last' must contain at least 1 character")
    if len(str(name_last)) > 50:
        raise InputError(
            description="The length of 'name_last' must not exceed 50 characters")

    # get the user id
    u_id = get_user_from_token(token)
    # get the user_dict that contains all user detail
    user_dict = abstractions.get_user(int(u_id))
    # update the user dict with new details
    user_dict['firstname'] = name_first
    user_dict['lastname'] = name_last
    abstractions.update_user(int(u_id), user_dict)

    return {}


def user_profile_setemail(token: str, email: str):

    # check the validity of token
    if token is None:
        raise InputError(description="Invalid Token")
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # check email format
    # Make a regular expression
    # for validating an Email
    regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    # pass the regualar expression
    # and the string in search() method
    if not re.search(regex, email):
        raise InputError(description="Invalid Email Address")

    # check if the email is already by another user
    u_ids = abstractions.get_all_user_ids()
    u_id = get_user_from_token(token)
    for item in u_ids:
        user_dict = abstractions.get_user(int(item))
        # check if the email is used by a registered user
        if user_dict['email'] == email and user_dict['user_id'] != u_id:
            raise InputError(description="Email Address Already Used")

    # update the user with the new email
    user_dict = abstractions.get_user(int(u_id))
    user_dict['email'] = email
    abstractions.update_user(int(u_id), user_dict)

    return {}


def user_profile_sethandle(token: str, handle_str: str):

    # check the validity of token
    if not check_valid_token(token):
        raise InputError(description="Invalid Token")

    # check the length of the handle_str
    if len(str(handle_str)) < 2:
        raise InputError(
            description="Handle must contain at least 2 characters")
    if len(str(handle_str)) > 50:
        raise InputError(
            description="The length of handle must not exceed 50 characters")

    # check if the handle is already used
    # get the user id
    u_id = get_user_from_token(token)
    user_ids = abstractions.get_all_user_ids()
    for user_id in user_ids:
        user_dict = abstractions.get_user(user_id)
        if user_dict['handle'] == handle_str and user_dict['user_id'] != u_id:

            raise InputError(description="Handle Already Used")

    # get the user details
    user_dict = abstractions.get_user(u_id)
    # update the handle
    user_dict['handle'] = handle_str
    abstractions.update_user(u_id, user_dict)

    return {}


def user_profile_uploadphoto(token: str, img_url: str, x_start: int, y_start: int, x_end: int, y_end: int):

    # check if the uploaded image is of jpg type
    if not 'jpg' in img_url:
        raise InputError(description="The Uploaded Photo Is Not JPG Type")

    # get the u_id
    u_id = get_user_from_token(token)
    # the profile photo for each user is named by
    # the concatenation of 'photo' and u_id
    # hence the profile photos are restored properly at local
    # check http status for img_url
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        # download the img to local as saved it as photo.jpg

        # Check if the static directory exists yet
        if not os.path.exists("static"):
            os.makedirs("static")
        # Check if the images directory exists yet
        if not os.path.exists("static/images"):
            os.makedirs("static/images")
        images_folder = Path('static/images')
        file_to_open = images_folder / f"photo{str(u_id)}.jpg"

        with open(file_to_open, 'wb+') as photo:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, photo)

    else:
        raise InputError(description="Invalid img_url")

    # get the dimension of the photo
    photo = Image.open(file_to_open)
    width, height = photo.size
    if x_start < 0 or x_end < 0:
        raise InputError(
            description="Unable to Crop The Image with The Given Positions 1 ")
    if y_start > 0 or y_end > 0:
        raise InputError(
            description="Unable to Crop The Image with The Given Positions 2")

    x_length = x_end - x_start
    y_length = y_end - y_start
    if x_length <= 0 or y_length >= 0:
        raise InputError(
            description="Unable to Crop The Image with The Given Positions 3")

    if x_end > width or x_start >= width:
        raise InputError(
            description="Unable to Crop The Image with The Given Positions 4")
    if (-1)*y_start >= height or (-1)*y_end > height:
        raise InputError(
            description="Unable to Crop The Image with The Given Positions 5")

    # crop the image
    top = (-1) * y_start
    left = x_start
    right = x_end
    bottom = (-1) * y_end
    cropped = photo.crop((left, top, right, bottom))
    cropped_file_to_save = images_folder / f"cropped{str(u_id)}.jpg"
    cropped.save(cropped_file_to_save)

    # update the user_dict with img_url
    user_dict = abstractions.get_user(u_id)
    user_data = user_dict
    user_data['profile_pic_url'] = f"cropped{str(u_id)}.jpg"
    abstractions.update_user(u_id, user_data)

    # upload the photo to the server
    return {}
