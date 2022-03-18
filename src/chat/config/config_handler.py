# ----------------------------------------------------
# To maintain getting config - 
# this module will help picking up wanted config parts
# from json file.
# ----------------------------------------------------

import os
import json


# absolute path of config file
_CONFIG_FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/config.json'


def get_config_data():
    with open(_CONFIG_FILE_PATH) as cfg_file:
        return json.load(cfg_file)
    

# ----------------------------------------------------
# implents getters for any config part
# ----------------------------------------------------

# possiblity of specifing databases name 
def get_db_data(db_name: str = None):
    key = 'db-manager-dbs-info'
    data = get_config_data()[key]

    if db_name:
        if db_name in data:
            data = data[db_name]
        else:
            print("[ERROR] key not found in json data")
            print("returning no data")
            return None

    return data    

# ...


def main():
    print("you should not be here!")
    exit()


if __name__ == "__main__":
    main()