import json
from typing import Dict, Any
from googleapiclient.errors import HttpError
from google_auth import GoogleAuth
from simple_logging import get_logger


class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, email_address: str = "timetable_calendar_sync@bridgend.ac.uk", credentials_filename: str = "service_calendar_credentials.json", credentials_dir: str = "credentials"):
        self.logger = get_logger(name="google_calendar_service", 
                                app_name="google-service", 
                                log_type="google-calendar")
        
        self.auth_service = GoogleAuth(
            credentials_dir=credentials_dir, 
            credentials_filename=credentials_filename, 
            email_address=email_address,
            scopes=self.SCOPES, 
            is_service_account=True
        ) 

        self.service = self.auth_service.build_auth_service(auth_type='calendar', auth_version='v3')
        
    def get_events(self, calendar_id: str, date_from: str, date_to: str, 
                  max_results: int = 100, 
                  search_query: str = None,
                  page_token: str = None,
                  single_events: bool = True,
                  order_by: str = 'startTime') -> Dict[str, Any]:
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=date_from,
                timeMax=date_to,
                maxResults=max_results,
                singleEvents=single_events,
                orderBy=order_by,
                q=search_query,
                pageToken=page_token
            ).execute()
            
            return events_result
            
        except HttpError as error:
            self.logger.error({
                "message": "Error retrieving events",
                "calendar_id": calendar_id,
                "error": str(error)
            })
            raise



calendar_service = GoogleCalendarService()