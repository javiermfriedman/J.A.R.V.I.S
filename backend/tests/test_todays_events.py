import json
from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def make_params(result_callback=None):
    """Build a minimal FunctionCallParams-like mock."""
    params = MagicMock()
    params.llm.push_frame = AsyncMock()
    params.result_callback = result_callback or AsyncMock()
    return params


def make_api_event(summary, start_iso, end_iso):
    """Return a Google Calendar API event dict with dateTime fields."""
    return {
        "summary": summary,
        "start": {"dateTime": start_iso},
        "end":   {"dateTime": end_iso},
    }


def make_all_day_event(summary, date_str):
    """Return a Google Calendar API event dict with date-only fields (all-day)."""
    return {
        "summary": summary,
        "start": {"date": date_str},
        "end":   {"date": date_str},
    }


FAKE_NOW = datetime(2025, 6, 15, 9, 0, 0)

SAMPLE_EVENTS = [
    make_api_event(
        "Standup",
        "2025-06-15T09:00:00+00:00",
        "2025-06-15T09:30:00+00:00",
    ),
    make_api_event(
        "Design Review",
        "2025-06-15T14:00:00+00:00",
        "2025-06-15T15:00:00+00:00",
    ),
]

MODULE = "google_calender"

PATCH_NOW = f"{MODULE}.datetime"
PATCH_CREDS = f"{MODULE}.get_google_credentials"
PATCH_BUILD = f"{MODULE}.build"


class TestGetTodaysEvents:

    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Result should be a valid JSON string."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat  # keep real parsing

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        parsed = json.loads(result)   # raises if not valid JSON
        assert isinstance(parsed, list)

    @pytest.mark.asyncio
    async def test_timed_events_are_included(self):
        """Timed events must appear in the filtered output."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        events = json.loads(result)
        summaries = [e["summary"] for e in events]
        assert "Standup" in summaries
        assert "Design Review" in summaries

    @pytest.mark.asyncio
    async def test_all_day_events_are_excluded(self):
        """Events with only a 'date' field (all-day) should be filtered out."""
        params = make_params()
        mixed = SAMPLE_EVENTS + [make_all_day_event("Holiday", "2025-06-15")]

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, mixed)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        events = json.loads(result)
        summaries = [e["summary"] for e in events]
        assert "Holiday" not in summaries
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_event_shape_has_required_keys(self):
        """Each filtered event must expose summary, start_time, end_time."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        for event in json.loads(result):
            assert "summary"    in event
            assert "start_time" in event
            assert "end_time"   in event

    @pytest.mark.asyncio
    async def test_time_format_is_12_hour(self):
        """start_time / end_time must follow 12-hour clock format (HH:MM AM/PM)."""
        import re
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        pattern = re.compile(r"^\d{2}:\d{2} (AM|PM)$")
        for event in json.loads(result):
            assert pattern.match(event["start_time"]), event["start_time"]
            assert pattern.match(event["end_time"]),   event["end_time"]

    @pytest.mark.asyncio
    async def test_empty_calendar_returns_empty_list(self):
        """When there are no events today, result should be an empty JSON list."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, [])

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        assert json.loads(result) == []

    @pytest.mark.asyncio
    async def test_missing_summary_falls_back_to_untitled(self):
        """Events without a summary key should default to 'Untitled Event'."""
        no_summary = {
            "start": {"dateTime": "2025-06-15T10:00:00+00:00"},
            "end":   {"dateTime": "2025-06-15T11:00:00+00:00"},
        }
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, [no_summary])

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        events = json.loads(result)
        assert events[0]["summary"] == "Untitled Event"

    @pytest.mark.asyncio
    async def test_result_callback_is_called_with_result(self):
        """result_callback must be awaited exactly once with the JSON string."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            result = await getTodaysEvents(params)

        params.result_callback.assert_awaited_once_with(result)

    @pytest.mark.asyncio
    async def test_tts_frame_is_pushed(self):
        """A TTSSpeakFrame must be pushed to the LLM before fetching events."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            await getTodaysEvents(params)

        params.llm.push_frame.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_api_called_with_todays_time_window(self):
        """The calendar API should be queried with midnight-to-midnight UTC range."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            mock_service = _setup_calendar_mock(mock_build, SAMPLE_EVENTS)

            from google_calender import getTodaysEvents
            await getTodaysEvents(params)

        call_kwargs = mock_service.events().list.call_args.kwargs
        assert call_kwargs["timeMin"].startswith("2025-06-15T00:00:00")
        assert call_kwargs["timeMax"].startswith("2025-06-16T00:00:00")
        assert call_kwargs["timeMin"].endswith("Z")
        assert call_kwargs["timeMax"].endswith("Z")

    @pytest.mark.asyncio
    async def test_google_api_error_is_handled(self):
        """A Google API exception should not propagate uncaught."""
        params = make_params()

        with patch(PATCH_NOW) as mock_dt, \
             patch(PATCH_CREDS), \
             patch(PATCH_BUILD) as mock_build:

            mock_dt.now.return_value = FAKE_NOW
            mock_dt.fromisoformat = datetime.fromisoformat

            mock_build.return_value.events.return_value.list.return_value \
                .execute.side_effect = Exception("API unavailable")

            from google_calender import getTodaysEvents
            try:
                await getTodaysEvents(params)
            except Exception as exc:
                pytest.fail(f"getTodaysEvents raised unexpectedly: {exc}")


def _setup_calendar_mock(mock_build, events):
    """Wire up mock_build so the calendar API returns `events`."""
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_service.events.return_value.list.return_value \
        .execute.return_value = {"items": events}

    return mock_service