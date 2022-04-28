# ----------------------------------------------------
# To maintain getting config - 
# this module will help picking up wanted config parts
# from json file.
# ----------------------------------------------------

import os
import json

# helper function
def _key_in_data(key, data):
    if key not in data:
        print(f"[ERROR] key {key}, not found in json data")
        return False
    
    return True


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

    if type:
        if not _key_in_data(type, data):
            return None

        return data[type]

    return data


#
#
#
def get_ui_data(which: str = None):
    key = 'uis'
    data = get_config_data()[key]

    if which:
        if not _key_in_data(which, data):
            return None

        return data[which]

    return data


#
#
#
def get_user_data_indexes():
    key = 'user_data_indexes'
    return get_config_data()[key]

#
#
#
def main():
    print("you should not be here!")
    exit()


if __name__ == "__main__":
    main()