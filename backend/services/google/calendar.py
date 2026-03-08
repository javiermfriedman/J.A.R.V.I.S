from pipecat.frames.frames import TTSSpeakFrame
from pipecat.services.llm_service import FunctionCallParams
from googleapiclient.discovery import build
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
from loguru import logger
from .auth import get_google_credentials

async def get_calender_events(params: FunctionCallParams):
    """get an array of calendar events for a given time range
    
    Args:
        params: start_date: The start date and time of the event (datetime object).
        end_date: The end date and time of the event (datetime object).
        Returns:
        str: JSON string of events for the given time range
    """
    try:
        logger.info("🛠 TOOL CALL: get_calender_events() invoked")

        # Bot speaks immediately before checking schedule
        await params.llm.push_frame(TTSSpeakFrame("Let me check your schedule diddy"))
        
        tz = ZoneInfo("America/New_York")
        start_date = datetime.fromisoformat(params.arguments.get("start_date", datetime.now().strftime("%Y-%m-%d-T%H:%M:%S")))
        end_date = datetime.fromisoformat(params.arguments.get("end_date", datetime.now().strftime("%Y-%m-%d-T%H:%M:%S")))

        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=tz)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=tz)
        time_min = start_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        time_max = end_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        logger.info(f"📅 Fetching calendar events for ({start_date.strftime('%Y-%m-%d-T%H:%M:%S')} to {end_date.strftime('%Y-%m-%d-T%H:%M:%S')})")
        
        # Get authenticated calendar service
        creds = get_google_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        # Fetch events from primary calendar
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Filter events to include only summary and simplified times (focusing on timed events)
        filtered_events = []
        for event in events:
            # We skip events without a 'dateTime' as they are typically all-day events that don't fit the '12:00 PM meeting' structure of the demo.
            start_time_str = event.get('start', {}).get('dateTime')
            end_time_str = event.get('end', {}).get('dateTime')
            summary = event.get('summary', 'Untitled Event')

            if start_time_str and end_time_str:
                # 1. Parse API string (removes 'Z' and converts to Python object)
                start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00')).astimezone()
                end_dt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00')).astimezone()
                
                # 2. Format for LLM readability
                start_time = start_dt.strftime("%I:%M %p")
                end_time = end_dt.strftime("%I:%M %p")

                filtered_events.append({
                    'summary': summary,
                    'start_time': start_time,
                    'end_time': end_time
                })
        
        result = json.dumps(filtered_events, indent=2)
        
        # NOTE: events variable in logger will still show max 50 events, but filtered_events is the concise list.
        logger.info(f"✅ Calendar events retrieved: {result}")
        await params.result_callback(result)
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get calendar events: {e}")
        error_result = f"Error retrieving calendar events: {str(e)}"
        await params.result_callback(error_result)
        return error_result


async def schedule_event(params: FunctionCallParams):
    """
    Book a Google Calendar event on the specified calendar.

    Args:
        service: An authenticated Google Calendar API service object.
        summary: The title of the event.
        start_date: The start date and time of the event (datetime object).
        end_date: The end date and time of the event (datetime object).
        description: A detailed description of the event (optional).
        timezone: The timezone for the event (ZoneInfo object).
                  This should match the timezone of your start_date/end_date if they are naive.
        calendar_id: The ID of the calendar to book the event on (defaults to 'primary').

    Returns:
        A dictionary containing information about the created event, or None if an error occurred.
    """

    try:

        logger.info("🛠 TOOL CALL: schedule_event() invoked")

        # Bot speaks immediately before checking schedule
        await params.llm.push_frame(TTSSpeakFrame("Let me book the event diddy"))
        
        summary = params.arguments.get("summary", "")
        start_date = datetime.fromisoformat(params.arguments.get("start_date", ""))
        end_date = datetime.fromisoformat(params.arguments.get("end_date", ""))
        description = params.arguments.get("description", "")
        email = params.arguments.get("email", "")
        location = params.arguments.get("location", "")


        timezone = "America/New_York"

        creds = get_google_credentials()
        service = build('calendar', 'v3', credentials=creds)

        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': timezone,
            },
            'sendNotifications': True,
        }

        if email:
            event['attendees'] = [{'email': email}]
        if location:
            event['location'] = location

        service.events().insert(calendarId='primary', body=event).execute()

        result = json.dumps(event, indent=2)

        logger.info(f"✅ Calendar event booked: {result}")
        await params.result_callback(result)
        return result

    except Exception as e:
        logger.error(f"❌ Failed to get calendar events: {e}")
        error_result = f"Error retrieving calendar events: {str(e)}"
        await params.result_callback(error_result)
        return error_result
