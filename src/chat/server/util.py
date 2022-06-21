# ----------------------------------------------------
# util
# utilites mainly for supplementing queries
# by adding things specific to data type 
# that query operates on
# ----------------------------------------------------

import os
from config import config_handler
import db_manager as dbm

# when creating new users, adding 'nnnn.' (where n - number) to his
# first 4 letters given in add new user form
def make_full_id(f_id: str) -> str:
    # since id of each row in table is numbered from 1 to n
    # and user_ids are numbered from 0000 to n
    # new user will get 000(last id from all_user_table) etc
    new_id_prefix = str(dbm.Main_DBM().last_added_user_id())
    # adding missing 0 to the front if needed 
    if len(new_id_prefix) != 4:
        new_id_prefix = '0' * (4 - len(new_id_prefix)) + new_id_prefix

    return  new_id_prefix + '.' + f_id


# get the chat id based on uids of users
# it will always look the same 
# so it can be created at any time anywhere where needed
def get_chat_id(first_id: str, second_id: str) -> str:
    # 'nnnn.aaaa's
    f_prefix = first_id[:4]
    s_prefix = second_id[:4]

    return str(f_prefix + s_prefix)


#
def create_file(path_with_file_included):
    os.system(f'touch {path_with_file_included}')


# will be changed ?
def make_conference_name(name):
    return name




if __name__ == "__main__":
    exit()