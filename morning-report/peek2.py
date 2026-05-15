#!/usr/bin/env python3
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = os.path.expanduser('~/.config/morning-report/token.json')
SPREADSHEET_ID = '1qJTdidlcdFFfvz3kMLNVHyhIgGQiLGh__wnVedf4_UQ'

creds = Credentials.from_authorized_user_file(TOKEN_FILE)
service = build('sheets', 'v4', credentials=creds)

result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='2026/5月!A1:M50'
).execute()

rows = result.get('values', [])
for i, row in enumerate(rows):
    # 只顯示有「家芸」的行，或前4行標題
    if i < 4 or (len(row) > 7 and '家芸' in row[7]):
        print(f"[{i+1}] {row}")
