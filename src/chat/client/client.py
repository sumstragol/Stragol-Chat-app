# ----------------------------------------------------
# client 
# 
# sends queries to the server
# ----------------------------------------------------

import json
import socket
import threading
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
login_queries = config_handler.get_queries_list('login')
messages_queries = config_handler.get_queries_list('messages')
users_queries = config_handler.get_queries_list('users')
menu_queries = config_handler.get_queries_list('menu')
profile_queries = config_handler.get_queries_list('profile')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(_ADDR)
print('[CLIENT] Successfully connected to a server.')
# when closing app - request will be send to remove user
# from currently connected users
client_user_id = ''




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


#
#
#
def _close_socket():
    if len(client_user_id) == 0:
        return

    content = {
        'query_family': login_queries['query_family'],
        'query_id':     login_queries['logout_request'],
        'user_id':      client_user_id
    }
    _send_any_query(content)


# ----------------------------------------------------
# implemenation for listening to responses
# ----------------------------------------------------

#
class Storage():
    def __init__(self, id, data) -> None:
        self.data_id = id
        self.data = data




responses_storage = []
pns_storage = []

#
_ACTIVE = True
def _listen_to_any_responses(condition_var):   
    global _ACTIVE
    while _ACTIVE:
        # wait till receive an message from server
        try:
            response_length = client.recv(_HEADER_SIZE).decode(_FORMAT)
        except:
            _ACTIVE = False
            break
        
        response_length = int(response_length)
        response = client.recv(response_length).decode(_FORMAT)
        data = json.loads(response)

        if 'query_id' in data:
            responses_storage.append(Storage(data['query_id'], data['answer']))
        elif 'pn_type' in data:
            condition_var.acquire()
            pns_storage.append(Storage(data['pn_type'], data['pn_data']))
            # notify thread getting the pns
            condition_var.notify_all()
            condition_var.release()
            
            
    
#
def _get_any_response(query_id: int):
    while _ACTIVE:
        for data in responses_storage:
            if data.data_id == query_id:
                responses_storage.remove(data)
                return data.data

        


# ----------------------------------------------------
# names of functions starts with keyword send,
# but actual functions does send nothing themselves.
# (sending happens in _send_any_query)
# purpose of that is to have friendly interface for
# the user, theres no reason to break this into seperate steps
# (prepare, attach values, etc..)
# from a user perspective. So it allows to convinently 
# do all things in one function call. 
# ----------------------------------------------------

# ----------------------------------------------------
# implementation for sending messages queries or
# anything closly related to message.
# ----------------------------------------------------

# when user want to chat somebody he creates chat room page,
# and its checked if conversation already happend if so - loading data
# 
def send_check_if_chat_exists(first_user_id: str, second_user_id: str):
    content = {
        'query_family':     messages_queries['query_family'],
        'query_id':         messages_queries['if_chat_exists'],
        'first_user_id':    first_user_id,
        'second_user_id':   second_user_id
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['if_chat_exists'])


# when table for chat doesnt exist yet (new conversation)
# it prepares for 'new chat' query 
def send_create_new_chat(first_user_id: str, second_user_id: str) -> None:
    content = {
        'query_family':     messages_queries['query_family'],
        'query_id':         messages_queries['create_new_chat'],
        'first_user_id':    first_user_id,
        'second_user_id':   second_user_id
    }    
    _send_any_query(content)

    return _get_any_response(messages_queries['create_new_chat'])


def send_create_new_room_query():
    pass


# when in database table for chat already exists
# it will only append new message to the table
def send_add_message(sender: str, receiver: str, chat_id: str, message: str) -> None:
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['add_message'],
        'sender':       sender,
        'receiver':     receiver,
        'chat_id':      chat_id,
        'message':      message
    }
    _send_any_query(content)
    
    return _get_any_response(messages_queries['add_message'])


# when entering the chat for the first time since lauching app
def send_chat_init_data_load(first_user_id: str, second_user_id):
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['chat_init_data_load'],
        'sender':       first_user_id,
        'receiver':     second_user_id
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['chat_init_data_load'])


def send_get_last_messages(chat_id: str):
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['get_last_messages'],
        'chat_id':      chat_id
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['get_last_messages'])


def send_init_general_chat():
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['init_general_chat'],
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['init_general_chat'])


def send_check_if_user_general_granted(user_id: str):
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['check_if_user_general_granted'],
        'user_id':      user_id
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['check_if_user_general_granted'])


def send_get_last_general_messages():
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['get_last_general_messages']
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['get_last_general_messages'])


def send_add_general_message(sender, message_content):
    content = {
        'query_family': messages_queries['query_family'],
        'query_id':     messages_queries['add_general_message'],
        'sender':       sender,
        'message':      message_content
    }
    _send_any_query(content)

    return _get_any_response(messages_queries['add_general_message'])

# ----------------------------------------------------
# implementation for sending login request
# ----------------------------------------------------

def send_login_request(data: dict):
    data['query_family'] = login_queries['query_family']
    data['query_id']     = login_queries['login_request']
    _send_any_query(data)

    return _get_any_response(login_queries['login_request'])


# ----------------------------------------------------
# implementation for menu queries
# ----------------------------------------------------

# menu - loading contacts
def send_load_contacts(my_user_id):
    content = {
        'query_family': menu_queries['query_family'],
        'query_id':     menu_queries['load_contacts'],
        "my_user_id":   my_user_id
    }
    _send_any_query(content)

    return _get_any_response(menu_queries['load_contacts'])


def send_change_status(user_id, status):
    content = {
        'query_family': menu_queries['query_family'],
        'query_id':     menu_queries['change_status'],
        'user_id':      user_id,
        'status':       status
    }
    _send_any_query(content)

    return _get_any_response(menu_queries['change_status'])


def send_get_other_statuses(user_id):
    content = {
        'query_family': menu_queries['query_family'],
        'query_id':     menu_queries['get_other_statuses'],
        'user_id':      user_id
    }
    _send_any_query(content)

    return _get_any_response(menu_queries['get_other_statuses'])

# ----------------------------------------------------
# implementation for queries adding new users
# ----------------------------------------------------

def send_add_new_user_query(data: dict):
    # whole data from form is already packed
    # adding headers 
    data['query_family'] = users_queries['query_family']
    data['query_id']     = users_queries['add_new_user']
    _send_any_query(data)

    return _get_any_response(users_queries['add_new_user'])


def send_check_if_login_is_in_use(login: str):
    content = {
        'query_family': users_queries['query_family'],
        'query_id':     users_queries['check_if_login_is_in_use'],
        'login':        login
    }
    _send_any_query(content)

    return _get_any_response(users_queries['check_if_login_is_in_use'])


# ----------------------------------------------------
# implementation for profile queries
# ----------------------------------------------------

def load_init_profile_data(user_id: str):
    content = {
        'query_family': profile_queries['query_family'],
        'query_id':     profile_queries['load_init_profile_data'],
        'user_id':      user_id
    }
    _send_any_query(content)

    return _get_any_response(profile_queries['load_init_profile_data'])


def send_profile_change(which: str, user_id: str, data: str):
    content = {
        'query_family': profile_queries['query_family'],
        'user_id': user_id
    }
    if which == 'password':
        content['query_id'] = profile_queries['change_password']
        content['new_value'] = data
        _send_any_query(content)
        return _get_any_response(profile_queries['change_password'])
    elif which == 'description':
        content['query_id'] = profile_queries['change_description']
        content['new_value'] = data
        _send_any_query(content)
        return _get_any_response(profile_queries['change_description'])
    elif which == 'personal_color':
        content['query_id'] = profile_queries['change_personal_color']
        content['new_value'] = data
        _send_any_query(content)
        return _get_any_response(profile_queries['change_personal_color'])
    else:
        print('wrong option, avaliable {password, description, personal_color}, youve chosen - ' + which)
        return None




# entry point for the client connection
# have to call this in order to use this modules functionality
# (sending messages is one part of the job, the second part is getting the responses) 
def start(condition_var):    
    thread = threading.Thread(target=_listen_to_any_responses, args=[condition_var])
    thread.start()


def stop():
    global client, _ACTIVE
    _ACTIVE = False
    _close_socket()
    client.close()
    
    
