# ----------------------------------------------------
#               RECENT FILES 
# to avoid looking for files in dbs each time when they
# are needed. ...  
#   
#   
#   
# ----------------------------------------------------
# todo - take time into account

from config import config_handler as ch

#
_RECENT_FILES_DATA = ch.get_recent_files_data()




class _Recent_Files_Data():
    def __init__(self, file_path, type, alias, used_count) -> None:
        self.file_path = file_path
        self.type = type
        self.alias = alias
        self.used_count = used_count




class Recent_Files():
    def __init__(self) -> None:
        self.recent_files = []
        self.storage_size = _RECENT_FILES_DATA['init_storage_size']
        self.storage_size_margin = _RECENT_FILES_DATA['storage_size_margin']


    def get_storage_size(self):
        return self.storage_size


    def resize_storage(self, new_size):
        if new_size > 0 and new_size <= _RECENT_FILES_DATA['max_possible_storage_size']:
            self.storage_size = new_size 


    def push_file(self, file_path, type = None, alias = None):
        self.recent_files.append(_Recent_Files_Data(file_path, type, alias, 1))


    def clear_storage(self):
        if len(self.recent_files) <= self.storage_size - self.storage_size_margin:
            return
        
        least_used = _RECENT_FILES_DATA['max_possible_storage_size'] + 1
        for data in self.recent_files:
            if data.used_count < least_used:
                least_used = data.used_count
        self.recent_files = [it for it in self.recent_files if it.used_count > least_used]
        

    def find_files(self, file_path = None, type = None, alias = None):
        look_up_words = []
        if file_path is not None: look_up_words.append(file_path)
        if type is not None: look_up_words.append(type)
        if alias is not None: look_up_words.append(alias)

        if not len(look_up_words):
            print('Speficy what file/files do you want to find')
            print("available keys: 'file_path', 'type', 'alias'")
            return []

        found_files = []
        for file_data in self.recent_files:
            for key in look_up_words:
                if file_path and key == file_data.file_path or \
                        type and key == file_data.type or \
                        alias and key == file_data.alias:
                    found_files.append(file_data)
                    file_data.used_count = file_data.used_count + 1
                    break

        self.clear_storage()
        return found_files




if __name__ == '__main__':
    exit()
    
