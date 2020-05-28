'''
Custom errors for the project
'''
from werkzeug.exceptions import HTTPException

# pylint: disable = W0107


class AccessError(HTTPException):
    '''
    User does not have permission to perform this operation.
    '''
    code = 400
    message = 'No message specified'


class InputError(HTTPException):
    '''
    User has entered incorrect input.
    '''
    code = 400
    message = 'No message specified'


class DataError(Exception):
    '''
    Raised when attempting to change protected data
    '''
    pass
