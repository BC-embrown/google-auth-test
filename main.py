from google_calendar_service import GoogleCalendarService


if __name__ == "__main__":
    google_calendar_service = GoogleCalendarService()
    events = google_calendar_service.get_events(calendar_id="primary", date_from="2025-04-01", date_to="2025-04-01")
    print(events)