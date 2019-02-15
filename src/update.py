from src.codeforces import *
from src.table import BeloiTable, BaseAccount


if __name__ == '__main__':
    data = [
        ('Балюк Игорь', 11, BaseAccount.Region.LYCEUM, 'Baliuk'),
        ('Бобень Вячеслав', 11, BaseAccount.Region.MINSK_OBL, 'DarkKeks'),
        ('Филинович Алексей', 11, BaseAccount.Region.BREST, 'aleex'),
        ('Ширма Кирилл', 11, BaseAccount.Region.BREST, 'Flyce'),
        ('Борисов Ярослав', 10, BaseAccount.Region.VITEBSK, 'Yaroslaff'),
        ('Денгалёв Даниил', 11, BaseAccount.Region.MOGILEV, 'programmer228'),
        ('Гришаев Никита', 11, BaseAccount.Region.MOGILEV, None),
        ('Кураш Владислав', 11, BaseAccount.Region.LYCEUM, None),
        ('Процкий Сергей', 10, BaseAccount.Region.LYCEUM, 'sergell'),
        ('Сечко Василий', 11, BaseAccount.Region.GRODNO, 'banany2001'),
        ('Акуленко Вячеслав', 11, BaseAccount.Region.GOMEL, 'Akel'),
        ('Пискевич Дариуш', 11, BaseAccount.Region.VITEBSK, 'Daryusz'),
        ('Костяной Андрей', 9, BaseAccount.Region.GOMEL, None),
        ('Мищенко Андрей', 10, BaseAccount.Region.GOMEL, 'andrew'),
    ]

    beloi_table = BeloiTable()

    base = beloi_table.platforms[0]

    cf = Codeforces()
    beloi_table.platforms.append(cf)

    for it in data:
        user = User(it[0])
        user.add_account(BaseAccount(base, it[1], it[2]))
        if it[3] is not None:
            user.add_account(NamedAccount(cf, it[3]))
        beloi_table.users.append(user)

    beloi_table.update()
