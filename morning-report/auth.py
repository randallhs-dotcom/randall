#!/usr/bin/env python3
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = os.path.expanduser('~/Downloads/client_secret_418579083071-3v0qk2vgno7phor935eamdf208piuiqf.apps.googleusercontent.com.json')
TOKEN_FILE = os.path.expanduser('~/.config/morning-report/token.json')

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    print('✅ 登入成功，Token 已儲存至', TOKEN_FILE)
    return creds

if __name__ == '__main__':
    authenticate()
