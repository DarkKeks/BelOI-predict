import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Hyperlink:
    PATTERN = '=HYPERLINK("{}";"{}")'

    def __init__(self, text, link):
        super().__init__()
        self.text = text
        self.link = link

    def __str__(self):
        return Hyperlink.PATTERN.format(self.link, self.text)


class Spreadsheet:
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

        data = [
            [column.header] + column.get_values(users) for platform in platforms for column in platform.get_columns()
        ]

        frozen_columns = len(data)

        contests = sorted([contest for platform in platforms for contest in platform.get_contests()],
                          key=lambda x: x.date)

        data += [[contest.header] + contest.get_values(users) for contest in contests]

        result = self.sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range='Main',
            valueInputOption='USER_ENTERED',
            body={
                'values': data,
                'majorDimension': 'COLUMNS'
            }
        ).execute()

        print('{0} cells updated.'.format(result.get('updatedCells')))

        self.update_table_formatting(sheet_id, frozen_columns=frozen_columns)
