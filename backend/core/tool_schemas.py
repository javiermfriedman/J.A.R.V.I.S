from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema




get_gmail_emails_tool = FunctionSchema(
    name="get_gmail_emails",
    description="Get the 2 most recent Gmail emails. Use this when the user asks about their emails, messages, or wants to check their inbox.",
    properties={},
    required=[],
)

send_gmail_email_tool = FunctionSchema(
    name="send_gmail_email",
    description="Send an email via Gmail. Use this when the user asks you to send, write, or compose an email to someone.",
    properties={
        "to": {
            "type": "string",
            "description": "The recipient's email address.",
        },
        "subject": {
            "type": "string",
            "description": "The subject line of the email.",
        },
        "body": {
            "type": "string",
            "description": "The body text of the email.",
        },
    },
    required=["to", "subject", "body"],
)

get_calender_events_tool = FunctionSchema(
    name="get_calender_events",
    description="Get an array of calendar events for a given time range. Use this when the user asks about their agenda, schedule, meetings, or what's on their calendar for a given time range.",
    properties={
        "start_date": {
            "type": "string",
            "description": "The start datetime in ISO 8601 format, e.g. '2025-06-15T09:00:00Z'.",
        },
        "end_date": {
            "type": "string",
            "description": "The end datetime in ISO 8601 format, e.g. '2025-06-15T17:00:00Z'.",
        },
    },
    required=["start_date", "end_date"],
)

schedule_event_tool = FunctionSchema(
    name="schedule_event",
    description="Schedule a Google Calendar event on the specified calendar. Use this when the user asks you to schedule a meeting, event, or appointment.",
    properties={
        "start_date": {
            "type": "string",
            "description": "The start datetime in ISO 8601 format, e.g. '2025-06-15T09:00:00Z'.",
        },
        "end_date": {
            "type": "string",
            "description": "The end datetime in ISO 8601 format, e.g. '2025-06-15T17:00:00Z'.",
        },
        "summary": {
            "type": "string",
            "description": "The summary of the event.",
        },
        "description": {
            "type": "string",
            "description": "The description of the event.",
        },
        "location": {
            "type": "string",
            "description": "The location of the event.",
        },
        "email": {
            "type": "string",
            "description": "an email adress to send the event invite to.",
        },
    },
    required=["start_date", "end_date", "summary", "description"],
)

fetch_all_known_contacts_tool = FunctionSchema(
    name="fetch_all_known_contacts",
    description="Fetch all known contacts from the contact book. Use this to see if the desired person is in the contact book and conact infomration e.g. email or phone number is already known",
    properties={},
    required=[],
)

get_contact_information_tool = FunctionSchema(
    name="get_contact_information",
    description="""JAVIS' contact book. Get a person contact information if user
    wants to send an email or a text check to see if the person is in the 
    contact book.If the person is not in the contact book, return Person name 
    not found in contact book.""",
    properties={
        "name": {
            "type": "string",
            "description": "The name/alias/nickname of the person to get contact information for.",
        },
    },
    required=["name"],
)

tools = ToolsSchema(standard_tools=[
    get_calender_events_tool,
    schedule_event_tool,
    get_gmail_emails_tool,
    send_gmail_email_tool,
    get_contact_information_tool,
])
