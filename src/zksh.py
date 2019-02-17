import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from src import util
from src.main import Platform, Contest, NamedAccount, GenericColumn


class ZKSH(Platform):
    config = Path('data/zksh.json')

    def __init__(self):
        super().__init__('zksh')
        self.contests = {}

    def process_user(self, user, data):
        if not self.user_has_account(user):
            account = self.find_user(user)
            if account is not None:
                user.add_account(account)

    def find_user(self, user):
        formatted_name = f"{user.accounts['base'].name} {user.accounts['base'].surname}"
        results = []
        for contest_id, contest in self.contests.items():
            for name in contest.results:
                ratio = fuzz.ratio(name.lower(), formatted_name.lower())
                if ratio >= 80:
                    results.append((name, ratio))
        if len(results):
            best = max(results, key=lambda x: x[1])
            return NamedAccount(self, best[0])
        return None

    def update_contests(self):
        with ZKSH.config.open('r') as f:
            config = json.load(f)
        for contest, params in config.items():
            if contest not in self.contests:
                name = params['name']
                date = datetime.utcfromtimestamp(params['date'])
                url = params['standings']
                self.contests[contest] = ZKSHContest(contest, name, date, url)

    def get_columns(self):
        return [
            GenericColumn('zksh-names', "Имя в ЗКШ", lambda user: f"{self.get_account(user).name}")
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
        rows = table.find_all('tr')[1:-3]
        for row in rows:
            data = row.find_all('td', class_='stnd')
            pos_match = re.search(r'\d+', data[0].text)
            if pos_match:
                pos = pos_match.group(0)
                name = re.search(r'.+(?=\s\(\d+\))', data[1].text).group(0)
                self.results[name] = pos

    def get_values(self, users):
        res = [self.results.get(user.accounts['zksh'].name, '')
               if 'zksh' in user.accounts and isinstance(user.accounts['zksh'], NamedAccount) else ''
               for user in users]
        return util.renumber(res)
