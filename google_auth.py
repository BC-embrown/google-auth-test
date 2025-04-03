from __future__ import print_function
import os.path, time
from simple_logging import get_logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class GoogleAuth:
    def __init__(self, scopes=None, email_address=None, credentials_dir=None, token_filename='token.json', credentials_filename='credentials.json', is_service_account=False):
        if scopes == None:
            raise Exception(f"Google Auth module - No scopes passed in")
        self.logger = get_logger(name='google-auth', app_name='google-service', log_type='google-auth') 
        self.logger.info({'message':f"Base directory: {BASE_DIR}"})
        self.scopes = scopes
        self.credentials_dir = os.path.join(BASE_DIR, credentials_dir) or BASE_DIR
        self.logger.info({'message':f"Credentials directory: {self.credentials_dir}"})
        self.token_location = os.path.join(self.credentials_dir, token_filename)
        self.logger.info({'message':f"Token location: {self.token_location}"})
        self.credentials_location = os.path.join(self.credentials_dir, credentials_filename)
        self.logger.info({'message':f"Credentials location: {self.credentials_location}"})
        self.is_service_account = is_service_account
         
        self.email_address = email_address
        self.credentials = None

    def build_auth_service(self, auth_type='sheets', auth_version='v4' ):
        creds = None
        if self.is_service_account:
            self.logger.info({'message':f"Building service account credentials"})
            creds = service_account.Credentials.from_service_account_file(self.credentials_location, scopes=self.scopes, subject=self.email_address)
        else:
            if os.path.exists(self.token_location):
                creds = Credentials.from_authorized_user_file(self.token_location, self.scopes)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(self.credentials_location):
                        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_location, self.scopes)
                        creds = flow.run_local_server(port=0)
                    else:
                        self.logger.error({'message':f"Credentials file not found at {self.credentials_location}"})
                        raise FileNotFoundError(f"Credentials file not found at {self.credentials_location}")

                with open(self.token_location, 'w') as token:
                    token.write(creds.to_json())

        try:
            if self.email_address:
                self.logger.info({'message':f"Adding subject to credentials: {self.email_address}"})
                creds = creds.with_subject(self.email_address)
                self.logger.info({'message':f"Credentials: {creds}"})
                resource = build(auth_type, auth_version, credentials=creds)
                self.credentials = creds
            return resource
        except HttpError as err:
            self.logger.error({'message':f"HTTP Error occurred: {err}"})
            raise

    def build_service_account_auth(self, auth_type='calendar',auth_version='v3'):
    
        service_account_key_file = 'credentials/service_calendar_credentials.json'
        api_scopes = ['https://www.googleapis.com/auth/calendar.events']

        user_to_impersonate = 'timetable_calendar_sync@bridgend.ac.uk'

        credentials = service_account.Credentials.from_service_account_file(
            service_account_key_file,
            scopes=api_scopes,
        )

        credentials = credentials.with_subject(user_to_impersonate)

        return build(auth_type, auth_version, credentials=credentials)

    def exponential_backoff(self, api_function, *args, max_retries=10, initial_delay=1, **kwargs):
        retry_delay = initial_delay

        for retry in range(max_retries):
            try:
                result = api_function(*args, **kwargs)
                return result
            except HttpError as error:
                if error.resp.status == 429:  # HTTP status code for rate limit exceeded
                    self.logger.error({'message':f"Rate limit exceeded. Retrying in {retry_delay} seconds..."})
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise  # Raise other HTTP errors

        raise Exception(f"Max retries ({max_retries}) exceeded.")

if __name__ == "__main__":
    auth = GoogleAuth(
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'],
        credentials_dir='/path/to/custom/credentials/dir'
    )
    service = auth.build_auth_service('sheets', 'v4')