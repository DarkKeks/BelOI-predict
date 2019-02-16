from enum import Enum

from src.main import Platform, GenericColumn, Account, User
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

    def __init__(self, platform, name, surname, grade, region):
        super().__init__(platform)
        self.name = name
        self.surname = surname
        self.grade = grade
        self.region = region


class BasePlatform(Platform):

    def __init__(self):
        super().__init__('base')

    def process_user(self, user, data):
        if not self.user_has_account(user):
            user.add_account(BaseAccount(self,
                                         data['name'],
                                         data['surname'],
                                         data['grade'],
                                         BaseAccount.Region[data['region']]))

    def get_columns(self):
        # Generating columns every call because you are unable to pickle lambdas :(
        return [
            GenericColumn('user', 'Имя', lambda user: f"{self.get_account(user).name} {self.get_account(user).surname}"),
            GenericColumn('grade', 'Класс', lambda user: self.get_account(user).grade),
            GenericColumn('grade', 'Область', lambda user: self.get_account(user).region)
        ]


class BeloiTable:

    def __init__(self):
        self.users = {}
        self.platforms = {}
        self.add_platform(BasePlatform())

        self.spreadsheet = Spreadsheet()
        self.spreadsheet.auth()

    def add_platform(self, platform):
        self.platforms[platform.name] = platform

    def add_user(self, unique_id, data):
        if unique_id not in self.users:
            user = User(data)
            for platform in self.platforms.values():
                platform.process_user(user, data)
            self.users[unique_id] = user

    def get_platform(self, name):
        return self.platforms.get(name)

    def update_platforms(self):
        for platform in self.platforms.values():
            platform.update_contests()

    def update(self):
        for platform in self.platforms.values():
            platform.update_contests()
            for user in self.users:
                platform.process_user(user, user.data)
        self.spreadsheet.write('Main', self.users.values(), self.platforms.values())
