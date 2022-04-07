# ----------------------------------------------------
# module for handling databases
# ----------------------------------------------------

import sqlite3
from config import config_handler as ch
import util


_SERVER_RESPOND_MESSAGES = ch.get_server_respond_messages()
# queries list
_QL_MESSAGES = ch.get_queries_list('messages')
_QL_USERS = ch.get_queries_list('users')

# ----------------------------------------------------
# implementing seperate classes for each database.
# 
# every class will derive from DB_Manager
# and will differ only in functions that will
# execute queries.
# ----------------------------------------------------

class DB_Manager():
    def __init__(self, name: str) -> None:
        self.db_data = ch.get_db_data(name)
        if not self.db_data:
            print('[ERROR] bad database name provided')
            return

        self.conn = sqlite3.connect(self.db_data['database_full_path'], check_same_thread = False)
        self.cur = self.conn.cursor()


class Main_DBM(DB_Manager):
    def __init__(self) -> None:
        self.name = 'main_db'
        super().__init__(self.name)


    def check_if_login_is_in_use(self, login: str) -> bool:
        return self.cur.execute(f"select id from users where login = '{login}' ").fetchone()


    def last_added_user_id(self):        
        return self.cur.execute(f"select id from all_users order by id DESC limit 1").fetchone()[0]
        

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
        if query_family == 'messages':
            if query_id == _QL_MESSAGES['create_new_chat']:
                self._create_new_chat(query_content)
                return -1
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
        pass


    def _create_new_room(self, query_content: dict) -> None:
        pass


    def _add_message(self, query_content: dict) -> bool:
        print(query_content)


    # ----------------------------------------------------
    # implemenation for queries related to chat
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


# ----------------------------------------------------
# some queries will be executed pretty rarely
# in comparison to others,
# so it doesnt require a whole class to wrap them in
# one place.
# ----------------------------------------------------
def exec_query(db_name, query, values=None):
    pass


def main():
    pass

if __name__ == '__main__':
    exit(main())