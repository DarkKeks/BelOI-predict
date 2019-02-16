from datetime import datetime


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
        try:
            return self.key(user)
        except AttributeError:
            return ''


class Contest(Column):
    def __init__(self, name, header, date=datetime.now()):
        super().__init__(name, header)
        self.date = date


class Platform:
    def __init__(self, name):
        self.name = name

    def process_user(self, user, data):
        pass

    def update_contests(self):
        pass

    def get_account(self, user):
        return user.accounts.get(self.name)

    def user_has_account(self, user):
        return self.name in user.accounts

    def get_columns(self):
        return []

    def get_contests(self):
        return []


class Account:
    def __init__(self, platform):
        self.platform = platform


class NamedAccount(Account):
    def __init__(self, platform, name):
        super().__init__(platform)
        self.name = name


class User:
    def __init__(self, data):
        self.data = data
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.platform.name] = account
