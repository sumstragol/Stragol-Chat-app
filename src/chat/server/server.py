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

os.system(f"freeport {_PORT}")
print(f'[SERVER] starting... ip: {_SERVER_IP}, port: {_PORT}.')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(_ADDR)
print('[SERVER] Ready.')

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
#
def respond_to_client(respond_id: int, data: dict):
    # ----------------------------------------------------
    # implemenation for response related to login form
    # ----------------------------------------------------

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_login_request']:
        login = data['login']
        password = data['password']
        result = dbm.Main_DBM().handle_login_request(login, password)
        response = {
            'answer': result
        }
        return _encode_any_content(response)


    # ----------------------------------------------------
    # implemenation for response related to menu
    # ----------------------------------------------------

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_load_contacts']:
        requested_by = data['my_user_id']
        result = dbm.Main_DBM().load_contacts(requested_by)
        response = {
            'answer': result
        }
        return _encode_any_content(response)

    # ----------------------------------------------------
    # implemenation for responses related to messages
    # ----------------------------------------------------

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_if_chat_exists']:
        fuid = data['first_user_id']
        suid = data['second_user_id']
        chat_id = dbm.Main_DBM().check_if_chat_exists(fuid, suid)
        response = {
            'answer': chat_id
        }
        return _encode_any_content(response)

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_create_new_chat']:
        fuid = data['first_user_id']
        suid = data['second_user_id']
        chat_id = dbm.Main_DBM().check_if_chat_exists(fuid, suid)
        result = True
        if chat_id is None: result = False
        response = {
            'answer': result
        }
        return _encode_any_content(response)

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_chat_init_data_load']:
        fuid = data['sender']
        suid = data['receiver']
        chat_init_data = dbm.Main_DBM().get_chat_init_data(fuid, suid)
        response = {
            'answer': chat_init_data
        }
        return _encode_any_content(response)

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_add_message']:
        response = {
            'answer': 1
        }
        return _encode_any_content(response)

    # ----------------------------------------------------
    # implemenation for responses related to users
    # ----------------------------------------------------

    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_check_if_login_is_in_use']:
        login = data['login']
        answer = dbm.Main_DBM().check_if_login_is_in_use(login)
        response = {
            'answer': answer
        }
        return _encode_any_content(response)
    
    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_add_new_user']:
        login = data['login']
        answer = dbm.Main_DBM().check_if_user_successfully_added(login)
        response = {
            'answer': answer
        }
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
            header, content = respond_to_client(respond_id, json.loads(query))
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