# pylint: disable = missing-docstring, invalid-name
import json
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS

from error import InputError


import auth
import channel
import channels
import hangman
import message
import other
import standup
import user
import users


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route('/channels/create', methods=['POST'])
def channels_create():
    data = json.loads(request.data)
    channel_id = channels.channels_create(
        str(data['token']),
        str(data['name']),
        bool(data['is_public'])
    )
    return dumps(channel_id)


@APP.route('/channels/listall', methods=['GET'])
def channels_listall():
    data = request.args
    listall = channels.channels_listall(
        str(data['token'])
    )
    return dumps(listall)


@APP.route('/channels/list', methods=['GET'])
def channels_list():
    data = request.args
    lst = channels.channels_list(
        str(data['token'])
    )
    return dumps(lst)


@APP.route('/user/profile', methods=['GET'])
def user_profile():
    data = request.args
    profile = user.user_profile(
        str(data['token']),
        int(data['u_id'])
    )
    base_url = request.base_url
    base_url = base_url[: -1 * len('/user/profile')]
    profile['profile_img_url'] = other.create_img_url(
        base_url, profile['profile_img_url'])
    return dumps(profile)


@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname():
    data = json.loads(request.data)
    result = user.user_profile_setname(
        str(data['token']),
        str(data['name_first']),
        str(data['name_last'])
    )
    return dumps(result)


@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail():
    data = json.loads(request.data)
    result = user.user_profile_setemail(
        str(data['token']),
        str(data['email'])
    )
    return dumps(result)


@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle():
    data = json.loads(request.data)
    result = user.user_profile_sethandle(
        str(data['token']),
        str(data['handle_str'])
    )
    return dumps(result)


@APP.route('/user/profile/uploadphoto', methods=['POST'])
def user_profile_uploadphoto():
    data = json.loads(request.data)
    result = user.user_profile_uploadphoto(
        str(data['token']),
        str(data['img_url']),
        int(data['x_start']),
        int(data['y_start']),
        int(data['x_end']),
        int(data['y_end'])
    )
    return dumps(result)


@APP.route('/users/all', methods=['GET'])
def users_all():
    data = request.args
    result = users.users_all(str(data['token']))
    base_url = request.base_url
    base_url = base_url[: -1 * len('/users/all')]
    for profile in result['users']:
        profile['profile_img_url'] = other.create_img_url(
            base_url, profile['profile_img_url'])
    return dumps(result)


# Auth Functions
@APP.route('/auth/login', methods=['POST'])
def auth_login():
    data = json.loads(request.data)
    result = auth.auth_login(
        data['email'], data['password'])
    return dumps(result)


@APP.route('/auth/logout', methods=['POST'])
def auth_logout():
    data = json.loads(request.data)
    result = auth.auth_logout(
        data['token']
    )
    return dumps(result)


@APP.route('/auth/register', methods=['POST'])
def auth_register():
    data = json.loads(request.data)
    result = auth.auth_register(
        data['email'], data['password'], data['name_first'], data['name_last'])
    return dumps(result)


@APP.route('/auth/passwordreset/request', methods=['POST'])
def auth_password_reset_request():
    data = json.loads(request.data)
    result = auth.auth_password_reset_request(
        data['email'])
    return dumps(result)


@APP.route('/auth/passwordreset/reset', methods=['POST'])
def auth_password_reset():
    data = json.loads(request.data)
    result = auth.auth_password_reset(
        data['reset_code'], data['new_password'])
    return dumps(result)

# Channels
@APP.route('/channel/invite', methods=['POST'])
def channel_invite():
    data = json.loads(request.data)
    result = channel.channel_invite(
        data['token'], data['channel_id'], data['u_id'])
    return dumps(result)


@APP.route('/channel/details', methods=['GET'])
def channel_details():
    data = request.args
    result = channel.channel_details(data['token'], data['channel_id'])
    base_url = request.base_url
    base_url = base_url[: -1 * len('/channel/details')]
    for profile in result['owner_members']:
        filename = profile['profile_img_url']
        profile['profile_img_url'] = other.create_img_url(
            base_url, filename)
    for profile in result['all_members']:
        profile['profile_img_url'] = other.create_img_url(
            base_url, filename)
    return dumps(result)


@APP.route('/channel/messages', methods=['GET'])
def channel_messages():
    data = request.args
    result = channel.channel_messages(
        data['token'], data['channel_id'], data['start'])
    return dumps(result)


@APP.route('/channel/leave', methods=['POST'])
def channel_leave():
    data = json.loads(request.data)
    result = channel.channel_leave(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/channel/join', methods=['POST'])
def channel_join():
    data = json.loads(request.data)
    result = channel.channel_join(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/channel/addowner', methods=['POST'])
def channel_addowner():
    data = json.loads(request.data)
    result = channel.channel_addowner(
        data['token'], data['channel_id'], data['u_id'])
    return dumps(result)


@APP.route('/channel/removeowner', methods=['POST'])
def channel_removeowner():
    data = json.loads(request.data)
    result = channel.channel_removeowner(
        data['token'], data['channel_id'], data['u_id'])
    return dumps(result)


@APP.route('/search', methods=['GET'])
def search():
    data = request.args
    result = other.search(data['token'], data['query_str'])
    return dumps(result)


@APP.route('/workplace/reset', methods=['POST'])
def workplace_reset():
    result = other.workplace_reset()
    return dumps(result)


@APP.route('/standup/start', methods=['POST'])
def standup_start():
    data = json.loads(request.data)
    result = standup.standup_start(
        data['token'], data['channel_id'], data['length'])
    return dumps(result)


@APP.route('/standup/active', methods=['GET'])
def standup_active():
    data = request.args
    result = standup.standup_active(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/standup/send', methods=['POST'])
def standup_send():
    data = json.loads(request.data)
    result = standup.standup_send(
        data['token'], data['channel_id'], data['message'])
    return dumps(result)


@APP.route('/admin/userpermission/change', methods=['POST'])
def userpermission_change():
    data = json.loads(request.data)
    result = other.userpermission_change(
        data['token'], data['u_id'], data['permission_id'])
    return dumps(result)


@APP.route('/admin/user/remove', methods=['DELETE'])
def user_remove():
    data = json.loads(request.data)
    result = other.user_remove(data['token'], data['u_id'])
    return dumps(result)


@APP.route('/message/send', methods=['POST'])
def message_send():
    data = json.loads(request.data)
    result = message.message_send(
        data['token'], data['channel_id'], data['message'])
    return dumps(result)


@APP.route('/message/sendlater', methods=['POST'])
def message_sendlater():
    data = json.loads(request.data)
    result = message.message_sendlater(
        data['token'], data['channel_id'], data['message'], data['time_sent'])
    return dumps(result)


@APP.route('/message/react', methods=['POST'])
def message_react():
    data = json.loads(request.data)
    result = message.message_react(
        data['token'], data['message_id'], data['react_id'])
    return dumps(result)


@APP.route('/message/unreact', methods=['POST'])
def message_unreact():
    data = json.loads(request.data)
    result = message.message_unreact(
        data['token'], data['message_id'], data['react_id'])
    return dumps(result)


@APP.route('/message/pin', methods=['POST'])
def message_pin():
    data = json.loads(request.data)
    result = message.message_pin(data['token'], data['message_id'])
    return dumps(result)


@APP.route('/message/unpin', methods=['POST'])
def message_unpin():
    data = json.loads(request.data)
    result = message.message_unpin(data['token'], data['message_id'])
    return dumps(result)


@APP.route('/message/remove', methods=['DELETE'])
def message_remove():
    data = json.loads(request.data)
    result = message.message_remove(data['token'], data['message_id'])
    return dumps(result)


@APP.route('/message/edit', methods=['PUT'])
def message_edit():
    data = json.loads(request.data)
    result = message.message_edit(
        data['token'], data['message_id'], data['message'])
    return dumps(result)


@APP.route('/hangman/start', methods=['POST'])
def hangman_start():
    data = json.loads(request.data)
    result = hangman.hangman_start(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/hangman/active', methods=['GET'])
def hangman_active():
    data = request.args
    result = hangman.hangman_active(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/hangman/details', methods=['GET'])
def hangman_details():
    data = request.args
    result = hangman.hangman_details(data['token'], data['channel_id'])
    return dumps(result)


@APP.route('/hangman/guess', methods=['POST'])
def hangman_guess():
    data = json.loads(request.data)
    result = hangman.hangman_guess(
        data['token'], data['channel_id'], data['guess'])
    return dumps(result)


@APP.route('/hangman/answer', methods=['GET'])
def hangman_answer():
    data = request.args
    result = hangman.hangman_answer(
        data['token'], data['channel_id'], data['current_hangman_id'])
    return dumps(result)


if __name__ == "__main__":
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))
