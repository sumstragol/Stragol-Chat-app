# ----------------------------------------------------
# util
# utilites mainly for supplementing queries
# by adding things specific to data type 
# that query operates on
# ----------------------------------------------------

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


# generate chat id based on users ids
def gen_chat_id(first: str, second: str) -> str:
    pass








if __name__ == "__main__":
    exit()