from enum import Enum

from src.main import Platform, GenericColumn, Account
from src.spreadsheet import Spreadsheet


class BaseAccount(Account):

    class Region(str, Enum):
        MINSK = "Минск"
        MINSK_OBL = "Минская"
        BREST = "Брестская"
        GOMEL = "Гомельская"
        MOGILEV = "Могилёвская"
        VITEBSK = "Витебская"
        GRODNO = "Гродненская"
        LYCEUM = "Лицей БГУ"

    def __init__(self, platform, grade, region):
        super().__init__(platform)
        self.grade = grade
        self.region = region


class BasePlatform(Platform):

    def __init__(self):
        super().__init__('base')
        self.columns = [
            GenericColumn('user', 'Имя', lambda user: user.name),
            GenericColumn('grade', 'Класс', lambda user: user.accounts['base'].grade),
            GenericColumn('grade', 'Область', lambda user: user.accounts['base'].region)
        ]

    def get_columns(self):
        return self.columns


class BeloiTable:

    def __init__(self):
        self.users = []
        self.platforms = [
            BasePlatform()
        ]
        self.spreadsheet = Spreadsheet()
        self.spreadsheet.auth()

    def update(self):
        self.spreadsheet.write('Main', self.users, self.platforms)
