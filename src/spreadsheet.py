import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.score import ScoreColumn, ScorePlatform, GP30


class Hyperlink:
    PATTERN = '=HYPERLINK("{}";"{}")'

    def __init__(self, text, link):
        super().__init__()
        self.text = text
        self.link = link

    def __str__(self):
        return Hyperlink.PATTERN.format(self.link, self.text)


class Cell:
    def __init__(self, row=1, col=1, sheet=None):
        self.sheet = sheet
        self.row = row
        self.col = col

    def __str__(self):
        if self.sheet:
            return f"{self.sheet}!{Cell.idx_to_col(self.col)}{self.row}"
        return f"{Cell.idx_to_col(self.col)}{self.row}"

    def copy(self, row=None, col=None, sheet=None):
        result = Cell(self.row if not row else row,
                      self.col if not col else col,
                      self.sheet if not sheet  else sheet)
        return result

    def add(self, row=0, col=0):
        return Cell(self.row + row, self.col + col, self.sheet)

    def sub(self, row=0, col=0):
        return self.add(-row, -col)

    @staticmethod
    def idx_to_col(idx):
        result = ''
        while idx > 0:
            digit = (idx % 26)
            if digit == 0:
                result += 'Z'
                idx -= 26
            else:
                result += chr(ord('A') + digit - 1)
            idx //= 26
        return result[::-1]


class Spreadsheet:
    START_CELL = Cell()
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = '1HhSTgz9p87GJTSB-u2Y1jU19hJRIRNm_NWH7yfQHljM'

    def __init__(self):
        self.creds = None
        self.service = None
        self.sheets = None

    def auth(self):
        self.creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', Spreadsheet.SCOPES)
                self.creds = flow.run_local_server()

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheets = self.service.spreadsheets()

    def get_sheet(self, name):
        result = self.sheets.get(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
        ).execute()

        for sheet in result['sheets']:
            if sheet['properties']['title'] == name:
                return sheet['properties']['sheetId']

        result = self.sheets.batchUpdate(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            body={
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": name
                        }
                    }
                }]
            }
        )

        return result['replies']['addSheet']['properties']['sheetId']

    def update_table_formatting(self, sheet_id,
                                frozen_rows=1,
                                frozen_columns=1):
        self.sheets.batchUpdate(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            body={
                "requests": [{
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "horizontalAlignment": "CENTER",
                                "textFormat": {
                                    "fontSize": 11,
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
                    }
                }, {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {
                                "frozenRowCount": frozen_rows,
                                "frozenColumnCount": frozen_columns
                            }
                        },
                        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
                    }
                }]
            }
        ).execute()

        print('Format for sheet {} updated.'.format(sheet_id))

    def write(self, table_name, users, platforms):
        sheet_id = self.get_sheet(table_name)
        table_range = Spreadsheet.START_CELL.copy(sheet=table_name)

        data = []

        columns = [column for platform in platforms for column in platform.get_columns()]

        contests = [contest for platform in platforms for contest in platform.get_contests()]
        contests = sorted(contests, key=lambda x: x.date)

        contests_range = table_range.add(col=len(columns))

        for idx, column in enumerate(columns):
            data += [[column.header] + column.get_values(users, table_range.add(col=idx))]

        for idx, contest in enumerate(contests):
            data += [[contest.header] + contest.get_values(users, contests_range.add(col=idx))]

        result = self.sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range=str(table_range),
            valueInputOption='USER_ENTERED',
            body={
                'values': data,
                'majorDimension': 'COLUMNS'
            }
        ).execute()

        print(f"Updated {result.get('updatedCells')} cells")

        # adding one row to account for header
        self.update_score(contests_range.add(row=1), len(contests), len(users))

        frozen_columns = len(columns)
        self.update_table_formatting(sheet_id, frozen_columns=frozen_columns)

    def update_score(self, contests_range, cols, rows):
        score_sheet = self.get_sheet(ScoreColumn.sheet)

        gp30_range = Cell(sheet=ScoreColumn.sheet)
        gp30_end_range = gp30_range.add(row=len(GP30.scores) - 1)
        result = self.sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range=gp30_range,
            valueInputOption='USER_ENTERED',
            body={
                'values': [GP30.scores],
                'majorDimension': 'COLUMNS'
            }
        ).execute()

        print(f"Updated GP30 scores")

        data = []
        for col in range(cols):
            data += [[
                ScorePlatform.SCORE_FORMULA.format(
                    contests_range.add(col=col, row=row),
                    gp30_range,
                    gp30_end_range
                ) for row in range(rows)
            ]]

        result_range = contests_range.copy(sheet=ScoreColumn.sheet)
        result = self.sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range=str(result_range),
            valueInputOption='USER_ENTERED',
            body={
                'values': data,
                'majorDimension': 'COLUMNS'
            }
        ).execute()

        print(f"Updated {result.get('updatedCells')} cells")

        data = [
            [ScorePlatform.SUM_FORMULA.format(
                result_range.add(row=idx),
                result_range.add(row=idx, col=cols - 1)
            ) for idx in range(rows)]
        ]

        result = self.sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range=str(Cell(col=2, sheet=ScoreColumn.sheet)),
            valueInputOption='USER_ENTERED',
            body={
                'values': data,
                'majorDimension': 'COLUMNS'
            }
        ).execute()

        print("Updated sum cells")


