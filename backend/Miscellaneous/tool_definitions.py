from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema


get_calendar_events_tool = FunctionSchema(
    name="get_calendar_events",
    description="Get calendar events for TODAY. Use this when the user asks about their agenda, schedule, meetings, or what's on their calendar for today.",
    properties={},
    required=[],
)

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

tools = ToolsSchema(standard_tools=[
    get_calendar_events_tool,
    get_gmail_emails_tool,
    send_gmail_email_tool,
])
