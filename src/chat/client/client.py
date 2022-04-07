# ----------------------------------------------------
# client 
# 
# sends queries to the server
# ----------------------------------------------------

import json
from logging.config import listen
import socket
from config import config_handler

print('[CLIENT] Client, starting.')
print('[CLIENT] Loading settings.')

# server data
_SERVER_SETTINGS = config_handler.get_server_data()
_SERVER_IP = _SERVER_SETTINGS['ip']
_PORT = _SERVER_SETTINGS['port']
_ADDR = (_SERVER_IP, _PORT)
_HEADER_SIZE = _SERVER_SETTINGS['header_size']
_FORMAT = _SERVER_SETTINGS['format']

# queries
messages_queries = config_handler.get_queries_list('messages')
users_queries = config_handler.get_queries_list('users')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(_ADDR)
print('[CLIENT] Successfully connected to a server.')


# ----------------------------------------------------
# implemenation for sending client queries
# ----------------------------------------------------

def _encode_any_content(content):
    content = json.dumps(content)
    content = content.encode(_FORMAT)
    content_size = len(content)
    header = str(content_size).encode(_FORMAT)
    header += b' ' * (_HEADER_SIZE - len(header))

    return header, content


def _send_any_query(content) -> None:
    header, content = _encode_any_content(content)
    client.send(header)
    client.send(content)


# ----------------------------------------------------
# implemenation for listening to responses
# ----------------------------------------------------

def _listen_to_any_response():
    response_length = client.recv(_HEADER_SIZE).decode(_FORMAT)
    response_length = int(response_length)
    response = client.recv(response_length).decode(_FORMAT)
    
    return json.loads(response)['answer']



# ----------------------------------------------------
# implementation for sending messages queries or
# anything closly related to message.
# names of functions starts with keyword send,
# but actual functions does send nothing themselves.
# (sending happens in _send_any_query)
# purpose of that is to have friendly interface for
# the user, theres no reason to break this into seperate steps
# (prepare, attach values, etc..)
# from a user perspective. So it allows to convinently 
# do all things in one function call. 
# ----------------------------------------------------

# when table for chat doesnt exist yet (new conversation)
# it prepares for 'new chat' query 
def send_create_new_chat_query(first_person_id: str, second_person_id: str) -> None:
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':   messages_queries['create_new_chat']
    }    

    _send_any_query(content)


def send_create_new_room_query():
    pass


# when in database table for chat already exists
# it will only append new message to the table
def send_add_message_query(message: str, sender: str, chat_id: str) -> None:
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['add_message'],
        'sender':       sender,
        'chat_id':      chat_id,
        'content':      message
    }
    
    _send_any_query(content)


# only for a admin
def send_add_new_user_query(data: dict) -> None:
    # whole data from form is already packed
    # adding headers 
    data['query_family'] = users_queries['query_family']
    data['query_id']     = users_queries['add_new_user']

    _send_any_query(data)


# only for a admin
def send_check_if_login_is_in_use(login: str) -> bool:
    content = {
        'query_family': users_queries['query_family'],
        'query_id':     users_queries['check_if_login_is_in_use'],
        'login':        login
    }

    _send_any_query(content)

    return _listen_to_any_response()
