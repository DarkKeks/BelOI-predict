import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Spreadsheet:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = '1HhSTgz9p87GJTSB-u2Y1jU19hJRIRNm_NWH7yfQHljM'

    def __init__(self):
        self.creds = None
        self.service = None

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

    def write(self, table_name, users, columns):
        sheets = self.service.spreadsheets()

        data = [[column.header for column in columns]]
        for user in users:
            data.append([column.get_value(user) for column in columns])

        result = sheets.values().update(
            spreadsheetId=Spreadsheet.SPREADSHEET_ID,
            range=table_name,
            valueInputOption='USER_ENTERED',
            body={
                'values': data
            }
        ).execute()

        print('{0} cells updated.'.format(result.get('updatedCells')))
