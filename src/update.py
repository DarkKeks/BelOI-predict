from src.codeforces import *
from src.table import BeloiTable

if __name__ == '__main__':
    cf_names = [
        ('Лол', 'DarkKeks'),
        ('Кек', 'Daryusz'),
        ('Chebureck', 'andrew')
    ]

    beloi_table = BeloiTable()
    beloi_table.platforms.append(Codeforces())

    cf = Codeforces()

    for it in cf_names:
        user = User(it[0])
        user.add_account(Account(cf, it[1]))
        beloi_table.users.append(user)

    beloi_table.update()

