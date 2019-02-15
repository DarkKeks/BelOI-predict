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


class Contest(Column):
    def __init__(self, name, header):
        super().__init__(name, header)


class Platform:
    def __init__(self, name):
        self.name = name

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
    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.platform.name] = account
