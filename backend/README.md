# J.A.R.V.I.S — Backend

Python **FastAPI** service that runs the **Pipecat** voice pipeline (Deepgram STT → OpenAI LLM → ElevenLabs TTS) with tool calls into Google Calendar, Gmail, contacts, and local shutdown.

**Stack:** Python (see [`.python-version`](.python-version)), FastAPI, Pipecat, `uvicorn`.

---

## File Map
```text
backend/
├── .python-version
├── .gitignore
├── .env.example
├── requirements.txt
├── app/
│   ├── main.py
│   ├── agent/
│   │   ├── prompts.py
│   │   └── tool_schemas.py
│   ├── orchestrator/
│   │   └── bot.py
│   └── integrations/
│       ├── shutdown_jarvis.py
│       ├── contacts/
│       │   ├── contact.py
│       │   └── contact_book.py
│       └── google/
│           ├── auth.py
│           ├── calendar.py
│           ├── gmail.py
│           └── config/
│               ├── credentials.json   # gitignored — OAuth client secret
│               └── token.json         # gitignored — user OAuth token
└── tests/
    ├── test_google.py
    ├── test_schedule_event.py
    ├── test_gmail_send.py
    ├── test_busy_periods.py
    ├── test_todays_events.py
    └── test_twilio.py
```

### Root

| File | Purpose |
|------|---------|
| **`.python-version`** | Pinned Python version. |
| **`.env.example`** | Template for all API keys; copy to `.env`. |
| **`requirements.txt`** | All pip dependencies. |

### app/

| File | Purpose |
|------|---------|
| **`main.py`** | FastAPI app: CORS, `POST`/`PATCH` `/api/offer`, starts `bot` when a session is negotiated. |
| **`agent/prompts.py`** | Defines `JARVIS_SYSTEM_PROMPT` — persona, behavior, and tool cheat sheet. |
| **`agent/tool_schemas.py`** | Pipecat `FunctionSchema` / `ToolsSchema` definitions passed to the LLM. |
| **`orchestrator/bot.py`** | Pipecat pipeline (STT → LLM → TTS), registers integration functions, transport lifecycle. |

### integrations/

| File | Purpose |
|------|---------|
| **`shutdown_jarvis.py`** | `shutdown_system` tool: TTS line, optional audio, macOS terminal/browser teardown. |
| **`contacts/contact.py`** | `fetch_all_known_contacts` and `get_contact_information` tool implementations. |
| **`contacts/contact_book.py`** | Static contact records the tools read from. |
| **`google/auth.py`** | OAuth `InstalledAppFlow`, `get_google_credentials()`. |
| **`google/gmail.py`** | `get_gmail_emails`, `send_gmail_email` tool implementations. |
| **`google/calendar.py`** | `get_calendar_events`, `schedule_event` tool implementations. |
| **`google/config/credentials.json`** | Google OAuth client JSON — gitignored, create in Cloud Console. |
| **`google/config/token.json`** | User OAuth token written after first login — gitignored. |

### tests/

| File | Purpose |
|------|---------|
| **`test_google.py`** | OAuth + Calendar/Gmail API access (integration tests). |
| **`test_schedule_event.py`** | Creates a real calendar event via Google API. |
| **`test_gmail_send.py`** | Sends a real email via Gmail API. |
| **`test_busy_periods.py`** | Free/busy calendar query. |
| **`test_todays_events.py`** | Pytest + mocks for today's events / calendar response handling. |
| **`test_twilio.py`** | Placeholder — reserved for Twilio tests. |

---

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | GPT-4 access |
| `ELEVENLABS_API_KEY` | ✅ | Voice synthesis |
| `DEEPGRAM_API_KEY` | ✅ | Speech to text |
| `TWILIO_ACCOUNT_SID` | ⬜ | SMS (not yet live) |
| `CONFIG_PATH` | ⬜ | Path to Google OAuth credentials directory |

1. Copy **`.env.example`** → **`.env`** and fill in your keys.
2. Place OAuth **`credentials.json`** in `app/integrations/google/config/` (or point `CONFIG_PATH` to its directory). First successful auth writes **`token.json`** beside it.
3. Never commit `.env`, `credentials.json`, or `token.json` — all are gitignored.

---

## Running Locally

From **`backend/`**:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in keys
```

Start the API:
```bash
uvicorn app.main:app --reload --host localhost --port 8000
```

Then start the frontend in a separate terminal (see root README). Vite runs on `127.0.0.1:5741`. CORS is open for development.

---

## HTTP API

The React app targets **`http://localhost:8000`** by default.

| Method | Path | Role |
|--------|------|------|
| `POST` | `/api/offer` | Client sends WebRTC SDP offer; server returns SDP answer and `pc_id`. |
| `PATCH` | `/api/offer` | Client sends ICE candidates; completes NAT traversal so audio can flow. |

All conversation is voice-in / voice-out over the peer connection. No REST surface is used for chat text.

---

## Prompts & Tools

- **`agent/prompts.py`** — `JARVIS_SYSTEM_PROMPT`: persona, behavior rules, and a plain-language tool cheat sheet for the model.
- **`agent/tool_schemas.py`** — machine-readable `FunctionSchema` definitions Pipecat passes to the LLM.

**Adding a new tool:**

1. Implement the async function under `app/integrations/`.
2. Add a `FunctionSchema` in `tool_schemas.py` and append it to the `ToolsSchema` list.
3. Update `JARVIS_SYSTEM_PROMPT` in `prompts.py` to describe the new capability.
4. In `bot.py`, call `llm.register_function("<same_name>", your_function)` — name must exactly match the schema.

> ⚠️ If the name, schema, registration, or prompt drift apart the model may call the wrong tool or the function won't be exposed.

---

## Platform Notes

Developed and tested on **macOS**. Windows is not supported — path assumptions exist in `ignition/` and some integrations.