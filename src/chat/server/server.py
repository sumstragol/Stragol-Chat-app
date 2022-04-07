# ----------------------------------------------------
# socket server. 
# dedicated server for this chat app,
# transferring queries(messages, adding users, etc).
#
# when user 'hits enter'
# his action/event gets handled by the server.
# validiting and then performing requested queries
# ----------------------------------------------------

from email import header
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
    if respond_id == _SERVER_RESPOND_MESSAGES['respond_to_check_if_login_is_in_use']:
        login = data['login']
        answer = dbm.Main_DBM().check_if_login_is_in_use(login)
        print(answer)

        respond_message = {
            'answer': answer
        }

        return _encode_any_content(respond_message)

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
        print(f"{addr} {query}")
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