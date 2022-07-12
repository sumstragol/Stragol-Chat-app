# ----------------------------------------------------
# To maintain getting config - 
# this module will help picking up wanted config parts
# from json file.
# ----------------------------------------------------

import os
import json

# helper functions
def _key_in_data(key, data):
    if key not in data:
        print(f"[ERROR] key {key}, not found in json data")
        return False
    
    return True


def _type_of_data(type, data):
    if type:
        if not _key_in_data(type, data):
            return None

        return data[type]

    return data




# absolute path of config file
_CONFIG_FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/config.json'

#
#
#
def get_config_data():
    with open(_CONFIG_FILE_PATH) as cfg_file:
        return json.load(cfg_file)
    

# ----------------------------------------------------
# implents getters for any config part
# ----------------------------------------------------
# in every case first specify the key which matches with
# the key in a JSON file, then call get_config_data()
# to retrive value / object of that key.
# if key one expands to more keys (object containing object)
# specify which next key to fetch. if no key is specified in that
# case return whole object.  

# possiblity of specifing databases name 
def get_db_data(db_name: str = None):
    key = 'db_manager_dbs_info'
    data = get_config_data()[key]
    return _type_of_data(db_name, data)  


#
# 
#
def get_server_data():
    return get_config_data()['server_info']
    

#
# list of queries 
# for client and server to help
# communicating between them.
# optional key if only one
# type of queries needed.
def get_queries_list(type: str = None):
    key = 'queries_list'
    data = get_config_data()[key]
    return _type_of_data(type, data)

    
#
#
#
def get_pending_notifications_list(type: str = None):
    key = 'pending_notifications'
    return get_config_data()[key]


#
#
#
def get_pending_notifications_indexes_list(type: str = None):
    key = 'pending_notications_indexes'
    data = get_config_data()[key]
    return _type_of_data(type, data)   


#
#
#
def get_server_respond_messages():
    key = 'server_respond_messages'
    return get_config_data()[key]


#
#
#
def get_dbs_users_chat_data():
    key = 'dbs_users_chats'
    return get_config_data()[key]


#
#
#
def get_dbs_conferences_chats_data():
    key = 'dbs_conference_chats'
    return get_config_data()[key]


#
#
#
def get_active_statuses_list(what: str):
    key = 'active_statuses'
    data = get_config_data()[key]
    return _type_of_data(what, data)  


#
#
#
def main():
    exit()


if __name__ == "__main__":
    main()