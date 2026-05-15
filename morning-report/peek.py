#!/usr/bin/env python3
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = os.path.expanduser('~/.config/morning-report/token.json')
SPREADSHEET_ID = '1qJTdidlcdFFfvz3kMLNVHyhIgGQiLGh__wnVedf4_UQ'

creds = Credentials.from_authorized_user_file(TOKEN_FILE)
service = build('sheets', 'v4', credentials=creds)

# 先列出所有 sheet 名稱
spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
for s in spreadsheet['sheets']:
    props = s.get('properties', s.get('sheetProperties', {}))
    print(f"Sheet: {props.get('title')} (gid={props.get('sheetId')})")

print('\n--- 抓前 5 行資料（第一個 sheet）---')
sheet_title = spreadsheet['sheets'][0].get('properties', {}).get('title')
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f'{sheet_title}!A1:Z5'
).execute()
for row in result.get('values', []):
    print(row)
