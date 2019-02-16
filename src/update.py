import json
import pickle
from pathlib import Path

from src.codeforces import *
from src.table import BeloiTable
from src.zksh import ZKSH


class DataStorage:
    table_file = Path('data/table.pickle')
    users_file = Path('data/users.json')

    def __init__(self):
        if self.table_file.exists():
            try:
                with self.table_file.open('rb') as f:
                    self.table = pickle.load(f)
            except:
                self.table = self.init_table()
        else:
            self.table = self.init_table()

        self.update_users()

    @staticmethod
    def init_table():
        beloi_table = BeloiTable()

        beloi_table.add_platform(Codeforces())
        beloi_table.add_platform(ZKSH())

        return beloi_table

    def update_users(self):
        for it in self.get_users():
            unique_id = f"{it['surname']} {it['name']}"
            self.table.add_user(unique_id, it)

    def get_users(self):
        return json.load(self.users_file.open('r'))

    def save(self):
        with self.table_file.open('wb') as f:
            pickle.dump(self, f)


if __name__ == '__main__':
    data = DataStorage()

    data.table.update()

    data.save()
