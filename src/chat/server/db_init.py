# ----------------------------------------------------
# module to initial database system
# ----------------------------------------------------

import sqlite3
from config import config_handler


def _print_status_message(source: str):
    print(f'[DB_INIT] {source} successfully created.')



#
# all_users
#
def make_all_users(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS all_users
            (
                id integer primary key autoincrement not null,
                user_id varchar(9),
                role varchar(5)        
            )
        '''
    )
    # adding admin account as a default
    cur.execute(
        '''
            insert into all_users(user_id, role)
            values('0000.adad', 'admin')
        '''
    )
    conn.commit()

    _print_status_message("all_users")


#
# users
#
def make_users(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS users
            (
                id integer primary key autoincrement not null,
                user_id varchar(9),
                login varchar,
                password varchar
            )
        '''
    )
    # adding admin as a default
    cur.execute(
        '''
            insert into users(user_id, login, password)
            values('0000.adad', 'admin', 'admin')
        '''
    )
    conn.commit()

    _print_status_message("users")    


#
# profiles
#
def make_profiles(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS profiles
            (
                id integer primary key autoincrement not null,
                user_id varchar(9),
                name varchar, 
                surname varchar,
                position varchar,
                description varchar,
                image varchar,
                color varchar
            )
        '''
    )
    # adding admin profile as a default
    cur.execute(
        '''
            insert into profiles(user_id, name, surname, position, description, image)
            values('0000.adad', 'Mikolaj', 'Brozek', '', '', '')
        '''
    )
    conn.commit()

    _print_status_message("profiles")


#
# chat list
#
def make_chats_list(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS chats_list
            (
                id integer primary key autoincrement not null,
                chat_id varchar(8),
                first_user_id varchar(9),
                second_user_id varchar(9),
                path varchar
            )
        '''
    )
    conn.commit()

    _print_status_message("chats_list")

    


#
# conferences list
#
def make_conferences_list(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS conferences_list
            (
                id integer primary key autoincrement not null,
                conference_id varchar,
                creator varchar(9),
                path_to_db varchar
            )
        '''
    )
    conn.commit()

    _print_status_message("conferences_list")


#
# general chat data
# (table containing all messages)
def make_general_chat_data(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS general_chat_data
            (
                id integer primary key autoincrement not null,
                send_date text,
                sender varchar(9),
                message_content varchar,
                visible_flag int
            )
        '''
    )
    conn.commit()

    _print_status_message("general_chat_data")


#
# general chat granted users
# (list of user that can type on this chat)
def make_general_chat_granted_users(conn, cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS general_chat_granted_people
            (
                id integer primary key autoincrement not null, 
                user_id varchar(9),
                permission_end_date text
            )
        '''
    )
    cur.execute(
        '''
            insert into general_chat_granted_people(user_id, permission_end_date)
            values('0000.adad', '3000-01-01')
        '''
    )
    conn.commit()

    _print_status_message("general chat granted users")




def main():
    main_db_path = config_handler.get_db_data('main_db')['database_full_path']
    main_conn = sqlite3.connect(main_db_path)
    main_cur = main_conn.cursor()
    # 1
    make_all_users(main_conn, main_cur)
    # 2
    make_users(main_conn, main_cur)
    # 3 
    make_profiles(main_conn, main_cur)
    # 4
    make_chats_list(main_conn, main_cur)
    # 5
    make_conferences_list(main_conn, main_cur)
    
    general_chat_db_path = config_handler.get_db_data('general_chat_db')['database_full_path']
    gcdp_conn = sqlite3.connect(general_chat_db_path)
    gcdp_cur = gcdp_conn.cursor()
    # 6
    make_general_chat_data(gcdp_conn, gcdp_cur)
    # 7
    make_general_chat_granted_users(gcdp_conn, gcdp_cur)

if __name__ == '__main__':
    main()