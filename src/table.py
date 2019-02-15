from src.main import Platform, GenericColumn
from src.spreadsheet import Spreadsheet


class BeloiTable:

    class BasePlatform(Platform):
        def __init__(self):
            super().__init__('base')
            self.columns = [
                GenericColumn('user', 'Имя', lambda user: user.name)
            ]

        def get_columns(self):
            return self.columns

    def __init__(self):
        self.users = []
        self.platforms = [
            BeloiTable.BasePlatform()
        ]
        self.spreadsheet = Spreadsheet()
        self.spreadsheet.auth()

    def update(self):
        self.spreadsheet.write('Main', self.users, self.platforms)
