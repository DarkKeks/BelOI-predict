import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from src import util
from src.main import Platform, Contest, NamedAccount, GenericColumn


# FIXME Копипастить файлы очень классно
#  Кпоипачу фаыл каждый день
#  И вем советую

class ZKSH(Platform):
    config = Path('data/innop.json')

    def __init__(self):
        super().__init__('innop')
        self.contests = {}

    def process_user(self, user, data):
        if not self.user_has_account(user):
            account = self.find_user(user)
            if account is not None:
                user.add_account(account)

    def find_user(self, user):
        # formatted_name = f"{user.accounts['base'].name} {user.accounts['base'].surname}"
        # results = []
        # for contest_id, contest in self.contests.items():
        #     for name in contest.results:
        #         ratio = fuzz.ratio(name.lower(), formatted_name.lower())
        #         if ratio >= 80:
        #             results.append((name, ratio))
        # if len(results):
        #     best = max(results, key=lambda x: x[1])
        #     return NamedAccount(self, best[0])
        return None

    def update_contests(self):
        # with ZKSH.config.open('r') as f:
        #     config = json.load(f)
        # for contest, params in config.items():
        #     if contest not in self.contests:
        #         name = params['name']
        #         date = datetime.utcfromtimestamp(params['date'])
        #         url = params['standings']
        #         self.contests[contest] = ZKSHContest(contest, name, date, url)

    def get_columns(self):
        return [
            GenericColumn('innop-names', "Имя в Олимпиаде Иннополис", lambda user: f"{self.get_account(user).name}")
        ]

    def get_contests(self):
        return self.contests.values()


class ZKSHContest(Contest):

    def __init__(self, name, header, date, url):
        super().__init__(name, header, date)
        self.results = {}

        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='standings')
        rows = table.find_all('tr')[2:]
        for row in rows:
            rank = row.find(class_='rank')
            party = row.find(class_='party')
            pos_match = re.search(r'\d+', rank.text)
            if pos_match:
                pos = pos_match.group(0)
                name = re.search(r'(.+)\s(.+)(?=,\s\d+)', party.text)
                name = (name.group(1), name.group(1))
                self.results[name] = pos

    def get_values(self, users, start_cell):
        res = [self.results.get(user.accounts['innop'].name, '')
               if 'innop' in user.accounts and isinstance(user.accounts['innop'], NamedAccount) else ''
               for user in users]
        return util.renumber(res)
