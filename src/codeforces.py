import requests

from src import util
from src.main import *
from src.spreadsheet import Hyperlink


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

    @staticmethod
    def get_contests():
        return CodeforcesUtil.api_query(
            'contest.list'
        )


class Codeforces(Platform):
    profile_link_pattern = 'https://codeforces.com/profile/{}'
    contest_border = datetime(2019, 1, 1, 0, 0, 0)

    def __init__(self):
        super().__init__('codeforces')

        self.columns = [
            GenericColumn('cf-name', 'CF Name', self.link_from_user),
            CodeforcesRating(self)
        ]
        self.contests = {}

    def process_user(self, user, data):
        if not self.user_has_account(user) and 'codeforces' in data and data['codeforces'] is not None:
            user.add_account(NamedAccount(self, data['codeforces']))

    def update_contests(self):
        all_contests = CodeforcesUtil.get_contests()
        for contest in all_contests:
            if contest['id'] not in self.contests:
                contest_date = datetime.utcfromtimestamp(contest['startTimeSeconds'])
                if contest_date > self.contest_border and contest['phase'] == 'FINISHED':
                    self.contests[contest['id']] = CodeforcesContest(self, contest['name'], contest['id'], contest_date)

    def get_columns(self):
        return self.columns

    def get_contests(self):
        return self.contests.values()

    @staticmethod
    def link_from_user(user):
        if 'codeforces' in user.accounts:
            name = user.accounts['codeforces'].name
            return str(Hyperlink(name, Codeforces.profile_link_pattern.format(name)))
        return None


class CodeforcesRating(Column):
    def __init__(self, platform):
        super().__init__('cf-rating', 'CF Rating')
        self.platform = platform

    def get_values(self, users):
        accounts = [self.platform.get_account(user) for user in users]
        names = [account.name for account in accounts if
                 isinstance(account, NamedAccount)]
        info = CodeforcesUtil.get_info(names)
        data = {item['handle']: item['rating'] for item in info}
        return [data[account.name] if account is not None else '' for account in accounts]


class CodeforcesContest(Contest):
    def __init__(self, platform, name, contest_id, date):
        super().__init__('cf-{}'.format(contest_id), name, date)
        self.platform = platform
        self.name = name
        self.contest_id = contest_id
        self.results = {}

    def get_values(self, users):
        accounts = [self.platform.get_account(user) for user in users]
        names = [account.name for account in accounts if
                 isinstance(account, NamedAccount) and
                 account.name not in self.results]
        if len(names):
            standings = CodeforcesUtil.get_standings(self.contest_id, names)
            data = {}
            for row in standings['rows']:
                for item in row['party']['members']:
                    data[item['handle']] = row['rank']
            self.results.update(data)
        res = [self.results.get(account.name, '') if account is not None else '' for account in accounts]
        return util.renumber(res)
