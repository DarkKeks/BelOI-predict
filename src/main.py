from src.table import Spreadsheet


class BeloiTable:
    def __init__(self):
        self.users = []
        self.platforms = []
        self.spreadsheet = Spreadsheet()
        self.spreadsheet.auth()
        self.columns = [
            GenericColumn('user', 'Имя', lambda user: user.name)
        ]

    def update(self):
        columns = self.columns
        columns += sum([platform.get_columns() for platform in self.platforms], [])
        self.spreadsheet.write('Main', self.users, columns)


class Column:
    def __init__(self, name, header):
        self.name = name
        self.header = header

    def get_value(self, user):
        return None

    def get_values(self, users):
        return [self.get_value(user) for user in users]


class GenericColumn(Column):
    def __init__(self, name, header, key):
        super().__init__(name, header)
        self.key = key

    def get_value(self, user):
        return self.key(user)


class Platform:
    def __init__(self, name):
        self.name = name

    def get_columns(self):
        return []


class Account:
    def __init__(self, platform, name):
        self.platform = platform
        self.name = name


class User:
    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.platform.name] = account


codeforces = Platform('codeforces')

