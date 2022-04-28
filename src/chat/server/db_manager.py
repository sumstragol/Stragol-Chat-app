# ----------------------------------------------------
# module for handling databases
# ----------------------------------------------------

import sqlite3
from config import config_handler as ch
import util
from recent_files import Recent_Files
from datetime import datetime

_SERVER_RESPOND_MESSAGES = ch.get_server_respond_messages()
# queries list
_QL_LOGIN = ch.get_queries_list('login')
_QL_MENU = ch.get_queries_list('menu')
_QL_MESSAGES = ch.get_queries_list('messages')
_QL_USERS = ch.get_queries_list('users')
#
_DBS_USERS_CHATS_DATA = ch.get_dbs_users_chat_data()
#
recent_file_storage = Recent_Files()


# ----------------------------------------------------
# implementing seperate classes for each database.
# 
# every class will derive from DB_Manager
# and will differ only in functions that will
# execute queries.
# ----------------------------------------------------

class DB_Manager():
    def __init__(self, name: str = None, path: str = None) -> None:
        db_path = None
        self.db_data = None

        if path is not None:
            db_path = path

        if name is not None:
            self.db_data = ch.get_db_data(name)
            if not self.db_data:
                print('[ERROR] bad database name provided')
                return
            else:
                db_path = self.db_data['database_full_path']

        self.conn = sqlite3.connect(db_path, check_same_thread = False)
        self.cur = self.conn.cursor()




# seprate interface for chat dbs
# might add other spefic featuers to it in the future
class Chat_DB(DB_Manager):
    def __init__(self, path: str = None) -> None:
        super().__init__(path=path)


    def _init_table(self):
        self.cur.execute(
            '''
                CREATE TABLE IF NOT EXISTS chat_data
                (
                    id integer primary key autoincrement not null,
                    sent_date text,
                    sender varchar(9),
                    message_content varchar,
                    reaction int,
                    visiable_flag int,
                    seen_flag int
                )
            '''
        )
        self.conn.commit()

    
    def add_message(self, query_content: dict):
        sender = query_content['sender']
        message = query_content['message']

        self.cur.execute(
            f'''
                insert into chat_data(sent_date, sender, message_content,
                    reaction, visiable_flag, seen_flag
                )

                values(?, ?, ?, ?, ?, ?)
            ''',
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sender, message, 0, 1, 0)
        )
        self.conn.commit()




class Main_DBM(DB_Manager):
    def __init__(self) -> None:
        self.name = 'main_db'
        super().__init__(name = self.name)

    # ----------------------------------------------------
    #                   SERVER RESPONSE 
    # implemenation for queries to handle server responses
    # ----------------------------------------------------

    # ----------------------------------------------------
    # SERVER RESPONSE - MESSAGES
    # query implemenation for responses related to messages
    # ----------------------------------------------------

    def check_if_chat_exists(self, first_user_id: str, second_user_id: str):
        f = self.cur.execute(
            f'''
                select chat_id from chats_list where
                first_user_id = '{first_user_id}' and
                second_user_id = '{second_user_id}'
            '''
        ).fetchone()
        s = self.cur.execute(
            f'''
                select chat_id from chats_list where
                first_user_id = '{second_user_id}' and
                second_user_id = '{first_user_id}'
            '''
        ).fetchone()
        
        if f: return f[0]
        if s: return s[0]
        return None


    def get_chat_init_data(self, first_user_id: str, second_user_id: str):
        suid_data = self.cur.execute(
            f'''
                select name, surname, image from profiles where
                user_id = '{second_user_id}'
            '''
        ).fetchall()
        return suid_data

    # ----------------------------------------------------
    # SERVER RESPONSE - USERS
    # query implemenation for responses related to users
    # ----------------------------------------------------

    def check_if_login_is_in_use(self, login: str) -> bool:
        result = self.cur.execute(f"select id from users where login = '{login}'").fetchone()
        if result: return True
        else: return False


    # used when creating new user_id - jump to util.py for
    # better explanation 
    def last_added_user_id(self):        
        return self.cur.execute(f"select id from all_users order by id DESC limit 1").fetchone()[0]


    def check_if_user_successfully_added(self, login: str) -> bool:
        result = self.cur.execute(
            f'''
                select user_id from users 
                where login = '{login}'
            '''
        ).fetchone()

        if result is None: return False
        else: return True

    # ----------------------------------------------------
    # SERVER RESPONSE - LOGIN FORM
    # query implemenation for responses related to login form
    # ----------------------------------------------------


    # returns user_id of account if data is correct
    def handle_login_request(self, login: str, password: str):
        result = self.cur.execute(
            f'''
                select user_id from users where
                login = '{login}' and password = '{password}'
            '''
         ).fetchone()

        if result is not None:
            return result[0]
        else:
            return None

    # ----------------------------------------------------
    # SERVER RESPONSE - MENU
    # query implemenation for responses related to menu
    # ----------------------------------------------------
    
    def load_contacts(self, requested_by: str):
        result = self.cur.execute(f'''
                select user_id, name, surname from profiles
                where user_id != '{requested_by}'
            '''
        ).fetchall()
        return result
        

    # returns a positive int if server has to respond
    #
    # ----- probably will change in future
    # sometimes when handling a query its performing it right away,
    # but in some cases query 'request' is sent back to the server
    # and server is performing the query on its own by using
    # this module class for a query.
    #
    # 1 case - it just a wave message that action
    # has been completed, so a query can be executed here,
    # server will send a simple message 
    #
    # 2 case - server has to return some 
    # more structured data
    #
    def handle_query(self, query_content: dict) -> int:
        query_family = query_content['query_family']
        query_id = query_content['query_id']

        #
        if query_family == 'login':
            if query_id == _QL_LOGIN['login_request']:
                return _SERVER_RESPOND_MESSAGES['respond_to_login_request']
        #
        if query_family == 'menu':
            if query_id == _QL_MENU ['load_contacts']:
                return _SERVER_RESPOND_MESSAGES['respond_to_load_contacts']
        #
        if query_family == 'messages':
            if query_id == _QL_MESSAGES['chat_init_data_load']:
                return _SERVER_RESPOND_MESSAGES['respond_to_chat_init_data_load']
            if query_id == _QL_MESSAGES['if_chat_exists']:
                return _SERVER_RESPOND_MESSAGES['respond_to_if_chat_exists']
            if query_id == _QL_MESSAGES['create_new_chat']:
                self._create_new_chat(query_content)
                return _SERVER_RESPOND_MESSAGES['respond_to_create_new_chat']
            elif query_id == _QL_MESSAGES['create_new_room']: 
                self._create_new_room(query_content)
                return -1
            elif query_id == _QL_MESSAGES['add_message']: 
                self._add_message(query_content)
                return _SERVER_RESPOND_MESSAGES['respond_to_add_message']
        #
        elif query_family == 'users':
            if query_id == _QL_USERS['add_new_user']:
                self._add_new_user(query_content)
                return _SERVER_RESPOND_MESSAGES['respond_to_add_new_user']
            if query_id == _QL_USERS['remove_user']:
                self._remove_user(query_content)
                return _SERVER_RESPOND_MESSAGES['respond_to_remove_user']
            if query_id == _QL_USERS['check_if_login_is_in_use']:
                return _SERVER_RESPOND_MESSAGES['respond_to_check_if_login_is_in_use']


    # ----------------------------------------------------
    # implemenation for queries related to chat
    # ----------------------------------------------------

    def _create_new_chat(self, query_content: dict) -> None:
        fuid = query_content['first_user_id']
        suid = query_content['second_user_id']
        db_directory = _DBS_USERS_CHATS_DATA['path']
        new_chat_id = util.get_chat_id(fuid, suid)
        new_db_chat_path = db_directory + '/' + new_chat_id + '.db'

        self.cur.execute('''
                insert into chats_list(chat_id, first_user_id, second_user_id, path)
                values(?, ?, ?, ?)
            ''',
            (new_chat_id, fuid, suid, new_db_chat_path)
        )
        self.conn.commit()

        # create db file and table 
        util.create_db_users_chat_file(new_db_chat_path)
        chat_db = Chat_DB(new_db_chat_path)
        chat_db._init_table()
        

    def _create_new_room(self, query_content: dict) -> None:
        pass


    def _add_message(self, query_content: dict) -> bool:
        #sender = query_content['sender']
        chat_id = query_content['chat_id']
        print(f'alias {chat_id}')
        #message = query_content['message']
        # check if db with chat messages is in recent files
        # if not - getting the location of chats file by looking it up in main_db
        # and adding it to recent files
        db_chat_file_data = recent_file_storage.find_files(alias=chat_id)
        chat_file_path = ''
        if not len(db_chat_file_data):
            chat_file_path = self.cur.execute(
                f'''
                    select path from chats_list where
                    chat_id = '{chat_id}'
                '''
            ).fetchone()[0]
            recent_file_storage.push_file(file_path=chat_file_path, type='db_users_chat', alias=chat_id)
        else:
            chat_file_path = db_chat_file_data[0].file_path

        chat_db = Chat_DB(chat_file_path)
        chat_db.add_message(query_content)


    # ----------------------------------------------------
    # implemenation for queries related to users
    # ----------------------------------------------------

    def _add_new_user(self, query_content: dict) -> None:
        user_id       = query_content['id']
        user_id       = util.make_full_id(user_id)
        role          = query_content['role']
        login         = query_content['login']
        password      = query_content['password']
        name          = query_content['name']
        surname       = query_content['surname']
        position      = query_content['position']
        description   = query_content['description']
        image         = query_content['image']

        # all_users
        self.cur.execute('''
                insert into all_users(user_id, role)
                values(?, ?)
            ''', 
            (user_id, role)
        )
        # users
        self.cur.execute('''
                insert into users(user_id, login, password)
                values(?, ?, ?)
            ''',
            (user_id, login, password)
        )
        # profiles
        self.cur.execute('''
                insert into profiles(user_id, name, surname, position, description, image)
                values(?, ?, ?, ?, ?, ?)
            ''',
            (user_id, name, surname, position, description, image)
        )   
        self.conn.commit()


    def _remove_user(self, user_id) -> None:
        self.cur.execute(f'delete from all_users where user_id = { user_id }')
        self.cur.execute(f'delete from users where user_id = { user_id }')
        self.cur.execute(f'delete from profiles where user_id = { user_id }') 
        self.conn.commit()




def main():
    Main_DBM()._add_message({})


if __name__ == '__main__':
    exit(main())