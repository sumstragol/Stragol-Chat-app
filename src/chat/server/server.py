# ----------------------------------------------------
# socket server. 
# dedicated server for this chat app,
# transferring queries(messages, adding users, etc).
#
# when user 'hits enter'
# his action/event gets handled by the server.
# validiting and then performing requested queries
# ----------------------------------------------------

import json
import socket
import threading
import os

from config import config_handler
import db_manager as dbm

print('[SERVER] Server, starting.')
print('[SERVER] Loading settings.')

_SERVER_SETTINGS = config_handler.get_server_data()
_SERVER_IP = _SERVER_SETTINGS['ip']
_PORT = _SERVER_SETTINGS['port']
_ADDR = (_SERVER_IP, _PORT)
_HEADER_SIZE = _SERVER_SETTINGS['header_size']
_FORMAT = _SERVER_SETTINGS['format']
_SERVER_RESPOND_MESSAGES = config_handler.get_server_respond_messages()
_PN = config_handler.get_pending_notifications_list()
_ASL = config_handler.get_active_statuses_list('statuses')
_DBS_USERS_CHATS_DATA = config_handler.get_dbs_users_chat_data()

os.system(f"freeport {_PORT}")
print(f'[SERVER] starting... ip: {_SERVER_IP}, port: {_PORT}.')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(_ADDR)
print('[SERVER] Ready.')




# ----------------------------------------------------
#                   CONNECTED USERS
# ----------------------------------------------------

class User():
    def __init__(self, uid, conn, addr) -> None:
        self.user_id = uid
        self.conn = conn
        self.addr = addr
        self.active_status = _ASL['active']




class Connected_Users():
    def __init__(self) -> None:
        self.connected_users = []


    def __iter__(self):
        return self.connected_users.__iter__()

    
    def __next__(self):
        return self.connected_users.__next__()


    def append_user(self, new_user: User):
        self.connected_users.append(new_user)


    def find_user(self, user_id):
        for user in self.connected_users:
            if user.user_id == user_id:
                return user
        
        return None


    def remove_user(self, user_id):
        index = 0
        found = False
        for user in self.connected_users:
            if user.user_id == user_id:
                found = True
                break
            index += 1

        if found:
            self.connected_users.pop(index)


    def change_status(self, user_id, status):
        user = self.find_user(user_id)
        user.active_status = status

    


# users that are currently connected will
# receive push notifications
# - stores user_ids
users_list = Connected_Users()







#
main_db = dbm.Main_DBM()


#
#
#
def disconnect_handling(conn, addr):
    print(f"[SERVER] {addr} has disconnected.")
    conn.shutdown()
    conn.close()


#
#
#
def _encode_any_content(content):
    content = json.dumps(content)
    content = content.encode(_FORMAT)
    content_size = len(content)
    header = str(content_size).encode(_FORMAT)
    header += b' ' * (_HEADER_SIZE - len(header))

    return header, content


#
#
# send pn to one specific user
def _send_push_notification(user: User, pn_type, pn_data):
    message = {
        'pn_type':  pn_type,
        'pn_data':  pn_data,
    }
    header, content = _encode_any_content(message)
    user.conn.send(header)
    user.conn.send(content)


#
#
# send pn to every single user that is currenlty connected except given user_id.
# use case - changing_status
def _send_push_notification_to_all_but(except_user_id: str, pn_type, pn_data):
    for single_user in users_list:
        if single_user.user_id == except_user_id:
            continue

        _send_push_notification(single_user, pn_type, pn_data)


#
#
#
def respond_to_client(respond_id: int, data: dict, conn, addr):
    response = {
        'query_id': data['query_id']
    }

    # ----------------------------------------------------
    # implemenation for response related to login form
    # ----------------------------------------------------

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_login_request']:
        login = data['login']
        password = data['password']
        result = dbm.Main_DBM().handle_login_request(login, password)
        response['answer'] = result
        # if the result is user_id - user have successfully logged in
        # list this user as connected
        if result is not None:
            # append to connected users
            users_list.append_user(User(result, conn, addr))
            # send pn to other connected users
            pn_type = _PN['change_status_pn']
            pn_data = {
                'user_id':  result,
                'status':   _ASL['active']
            }
            _send_push_notification_to_all_but(result, pn_type, pn_data)
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_logout_request']:
        user_id = data['user_id']
        users_list.remove_user(user_id)
        pn_type = _PN['change_status_pn']
        pn_data = {
            'user_id':  user_id,  
            'status':   _ASL['inactive']
        }
        _send_push_notification_to_all_but(user_id, pn_type, pn_data)
        response['answer'] = True
        return _encode_any_content(response)


    # ----------------------------------------------------
    # implemenation for response related to menu
    # ----------------------------------------------------

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_load_contacts']:
        requested_by = data['my_user_id']
        result = dbm.Main_DBM().load_contacts(requested_by)
        response['answer'] = result
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_change_status']:
        requested_by = data['user_id']
        users_list.change_status(requested_by, data['status'])
        # first send to all other users
        pn_type = _PN['change_status_pn']
        pn_data = {
            'user_id': requested_by,
            'status': data['status']
        }
        _send_push_notification_to_all_but(requested_by, pn_type, pn_data)
        # response to user that requested status change
        response['answer'] = True
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_get_other_statuses']:
        requested_by = data['user_id']
        other_statuses = {}
        for user in users_list:
            if user.user_id != requested_by:
                other_statuses[user.user_id] = user.active_status
        response['answer'] = other_statuses
        return _encode_any_content(response)

    # ----------------------------------------------------
    # implemenation for responses related to messages
    # ----------------------------------------------------

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_if_chat_exists']:
        fuid = data['first_user_id']
        suid = data['second_user_id']
        chat_id = dbm.Main_DBM().check_if_chat_exists(fuid, suid)
        response['answer'] = chat_id
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_create_new_chat']:
        fuid = data['first_user_id']
        suid = data['second_user_id']
        chat_id = dbm.Main_DBM().check_if_chat_exists(fuid, suid)
        result = True
        if chat_id is None: result = False
        response['answer'] = result
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_chat_init_data_load']:
        fuid = data['sender']
        suid = data['receiver']
        chat_init_data = dbm.Main_DBM().get_chat_init_data(fuid, suid)
        response['answer'] = chat_init_data
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_add_message']:
        receiver = data['receiver']
        # check if user is connected
        # if true send pn to him
        # if false do nothing (?)
        temp_user = users_list.find_user(receiver)
        if temp_user:
            chat_id = data['chat_id']
            chat_path = _DBS_USERS_CHATS_DATA['path'] + chat_id + '.db'
            data = dbm.Chat_DB(chat_path).get_last_message()
            _send_push_notification(temp_user, _PN['add_message_pn'], data)
        response['answer'] = True
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_get_last_messages']:
        chat_id = data['chat_id']
        chat_path = _DBS_USERS_CHATS_DATA['path'] + chat_id + '.db'
        last_messages = dbm.Chat_DB(chat_path).get_last_messages()
        response['answer'] = last_messages
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_init_general_chat']:
        data = dbm.General_Chat_DB().get_init_data()
        response['answer'] = data
        return _encode_any_content(response)
    
    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_check_if_user_general_granted']:
        user_id = data['user_id']
        answer = dbm.General_Chat_DB().check_if_user_granted(user_id)
        response['answer'] = answer
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_add_general_message']:
        sender = data['sender']
        message = data['message']
        # add message to database
        content = {
            "sender":   sender,
            "message":  message    
        }
        dbm.General_Chat_DB().add_message(content)
        # send pn to all other users
        last_message = dbm.General_Chat_DB().get_last_message()
        _send_push_notification_to_all_but(sender, _PN['add_general_message_pn'], last_message)
        # send response to the user
        response['answer'] = True
        return _encode_any_content(response)

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_get_last_general_messages']:
        last_messages = dbm.General_Chat_DB().get_last_messages()
        response['answer'] = last_messages
        return _encode_any_content(response)


    # ----------------------------------------------------
    # implemenation for responses related to users
    # ----------------------------------------------------

    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_check_if_login_is_in_use']:
        login = data['login']
        answer = dbm.Main_DBM().check_if_login_is_in_use(login)
        response['answer'] = answer
        return _encode_any_content(response)
    
    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_add_new_user']:
        login = data['login']
        answer = dbm.Main_DBM().check_if_user_successfully_added(login)
        response['answer'] = answer
        return _encode_any_content(response)
    
    # ----------------------------------------------------
    # implemenation for responses related to profile
    # ----------------------------------------------------
    
    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_change_password'] \
    or respond_id == _SERVER_RESPOND_MESSAGES['respond_to_change_description'] \
    or respond_id == _SERVER_RESPOND_MESSAGES['respond_to_change_personal_color']:
        response['answer'] = True
        return _encode_any_content(response)
    
    elif respond_id == _SERVER_RESPOND_MESSAGES['respond_to_load_init_profile_data']:
        user_id = data['user_id']
        result = dbm.Main_DBM().load_init_profile_data(user_id)
        response['answer'] = result
        return _encode_any_content(response)






# 
#
#
def connection_handling(conn, addr):    
    joined = True
    while joined:
        message_length = conn.recv(_HEADER_SIZE).decode(_FORMAT)

        if not message_length:
            return

        message_length = int(message_length)
        query = conn.recv(message_length).decode(_FORMAT)
        # developing only
        print(f" SERVER QUERY: {addr} {query}\n")
        respond_id = main_db.handle_query(json.loads(query))
        
        if respond_id > -1:
            header, content = respond_to_client(respond_id, json.loads(query), conn, addr)
            conn.send(header)
            conn.send(content)
            


    disconnect_handling(conn, addr)


#
#
#
def start():
    print('[SERVER] now listening for a new connections.')
    server.listen()

    while True:
        connected_socket, address = server.accept()
        thread = threading.Thread(target=connection_handling, args=(connected_socket, address))
        thread.start()
        print(f"[SERVER] new connection, {address} has connected.")


def main():
    start()


if __name__ == '__main__':
    main()