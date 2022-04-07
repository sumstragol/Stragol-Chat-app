# ----------------------------------------------------
# module to initial database system
# ----------------------------------------------------

import sqlite3
from config import config_handler


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
                image varchar
            )
        '''
    )

    # adding admin profile as a default
    cur.execute(
        '''
            insert into profiles(user_id, name, surname, position, description, image)
            values('0000.adad', '', '', '', '', '')
        '''
    )

    conn.commit()


def main():
    db_path = config_handler.get_db_data('main_db')['database_full_path']

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor();

    # 1
    make_all_users(connection, cursor)
    # 2
    make_users(connection, cursor)
    # 3 
    make_profiles(connection, cursor)



if __name__ == '__main__':
    main()