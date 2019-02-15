import requests
from src.main import *


class CodeforcesUtil:

    @staticmethod
    def api_query(method, **kwargs):
        url = 'https://codeforces.com/api/{}?{}'.format(
            method,
            '&'.join(['='.join([key, str(val)]) for key, val in kwargs.items()]))
        result = requests.get(url).json()
        if result['status'] != 'OK':
            raise Exception(result['comment'])

        print(result)
        return result['result']

    @staticmethod
    def get_standings(contest_id, users):
        return CodeforcesUtil.api_query(
            'contest.standings',
            contestId=contest_id,
            handles=';'.join(users)
        )

    @staticmethod
    def get_info(users):
        return CodeforcesUtil.api_query(
            'user.info',
            handles=';'.join(users)
        )


class Codeforces(Platform):
    def __init__(self):
        super().__init__('codeforces')

        self.columns = [
            GenericColumn('cf-name', 'CF Name',
                          lambda user: user.accounts['codeforces'].name if 'codeforces' in user.accounts else None),
            CodeforcesRating(),
        ]
        self.contests = [
            CodeforcesContest('CF 538', 1114),
            CodeforcesContest('CF GR 1', 1110),
            CodeforcesContest('CF 537', 1111),
            CodeforcesContest('CF 536', 1106),
            CodeforcesContest('CF ED 59', 1107),
        ]

    def get_columns(self):
        return self.columns

    def get_contests(self):
        return self.contests


class CodeforcesRating(Column):
    def __init__(self):
        super().__init__('cf-rating', 'CF Rating')
        self.rating_cache = {}

    def get_values(self, users):
        accounts = [user.accounts['codeforces'] if 'codeforces' in user.accounts else None for user in users]
        names = [account.name for account in accounts if account is not None]
        info = CodeforcesUtil.get_info(names)
        data = {item['handle']: item['rating'] for item in info}
        return [data[account.name] if account is not None else None for account in accounts]


class CodeforcesContest(Contest):
    def __init__(self, name, contest_id):
        super().__init__('cf-{}'.format(contest_id), name)
        self.name = name
        self.contest_id = contest_id

    def get_values(self, users):
        accounts = [user.accounts['codeforces'] if 'codeforces' in user.accounts else None for user in users]
        names = [account.name for account in accounts if account is not None]
        standings = CodeforcesUtil.get_standings(self.contest_id, names)
        data = {}
        for row in standings['rows']:
            for item in row['party']['members']:
                data[item['handle']] = row['rank']
        return [data.get(account.name) if account is not None else None for account in accounts]
