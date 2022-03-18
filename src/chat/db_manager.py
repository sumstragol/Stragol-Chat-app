# ----------------------------------------------------
# module for handling databases
# ----------------------------------------------------

import sqlite3
from config import config_handler as ch

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

        self.conn = sqlite3.connect(self.db_data['database_full_path'])
        self.cur = self.conn.cursor()


class Main_DBM(DB_Manager):
    def __init__(self) -> None:
        self.name = 'main-db'
        super().__init__(self.name)
        

    def other_example(self):
        pass


# ----------------------------------------------------
# some queries will be executed pretty rarely
# in comparison to others,
# so it doesnt require a whole class to wrap them in
# one place.
# ----------------------------------------------------
def exec_query(db_name, query, values=None):
    pass


test = Main_DBM()
print(test.db_data)