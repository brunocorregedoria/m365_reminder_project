import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

from m365_reminder_project.api import get_access_token, call_graph_api, get_all_users, get_todays_events
from m365_reminder_project.models import Event
from config import Config

class TestM365Api(unittest.TestCase):

    @patch("requests.post")
    def test_get_access_token_success(self, mock_post):
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {"access_token": "fake_token"}
        
        Config.TENANT_ID = "test_tenant"
        Config.CLIENT_ID = "test_client_id"
        Config.CLIENT_SECRET = "test_client_secret"

        token = get_access_token()
        self.assertEqual(token, "fake_token")

    @patch("requests.post")
    def test_get_access_token_failure(self, mock_post):
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.RequestException("Connection error")
        
        Config.TENANT_ID = "test_tenant"
        Config.CLIENT_ID = "test_client_id"
        Config.CLIENT_SECRET = "test_client_secret"

        with self.assertRaises(requests.exceptions.RequestException):
            get_access_token()

    @patch("requests.get")
    def test_call_graph_api_get_success(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"value": []}

        token = "fake_token"
        endpoint = "/users"
        result = call_graph_api(token, endpoint)
        self.assertEqual(result, {"value": []})

    @patch("requests.get")
    def test_call_graph_api_get_http_error(self, mock_get):
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

        token = "fake_token"
        endpoint = "/nonexistent"
        with self.assertRaises(requests.exceptions.HTTPError):
            call_graph_api(token, endpoint)

    @patch("m365_reminder_project.api.call_graph_api")
    def test_get_all_users_success(self, mock_call_graph_api):
        mock_call_graph_api.return_value = {"value": [{"id": "1", "displayName": "User One"}]}
        token = "fake_token"
        users = get_all_users(token)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["displayName"], "User One")

    @patch("m365_reminder_project.api.call_graph_api")
    def test_get_todays_events_success(self, mock_call_graph_api):
        mock_call_graph_api.return_value = {"value": [
            {
                "id": "event1",
                "subject": "Meeting",
                "start": {"dateTime": "2025-06-11T09:00:00Z", "timeZone": "UTC"},
                "end": {"dateTime": "2025-06-11T10:00:00Z", "timeZone": "UTC"}
            }
        ]}
        token = "fake_token"
        user_id = "user123"
        events = get_todays_events(token, user_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["subject"], "Meeting")

class TestM365Utils(unittest.TestCase):

    def test_detect_conflicts_no_conflict(self):
        event1 = Event("1", "Meeting A", None, datetime(2025, 6, 11, 9, 0), datetime(2025, 6, 11, 10, 0), None, None, [], False)
        event2 = Event("2", "Meeting B", None, datetime(2025, 6, 11, 10, 0), datetime(2025, 6, 11, 11, 0), None, None, [], False)
        events = [event1, event2]
        from m365_reminder_project.utils import detect_conflicts
        conflicts = detect_conflicts(events)
        self.assertEqual(len(conflicts), 0)

    def test_detect_conflicts_with_conflict(self):
        event1 = Event("1", "Meeting A", None, datetime(2025, 6, 11, 9, 0), datetime(2025, 6, 11, 10, 30), None, None, [], False)
        event2 = Event("2", "Meeting B", None, datetime(2025, 6, 11, 10, 0), datetime(2025, 6, 11, 11, 0), None, None, [], False)
        events = [event1, event2]
        from m365_reminder_project.utils import detect_conflicts
        conflicts = detect_conflicts(events)
        self.assertEqual(len(conflicts), 1)
        self.assertIn((event1, event2), conflicts)

    def test_suggest_focus_blocks_full_day(self):
        events = []
        from m365_reminder_project.utils import suggest_focus_blocks
        focus_blocks = suggest_focus_blocks(events, start_hour=9, end_hour=17, min_block_duration_minutes=60)
        self.assertEqual(len(focus_blocks), 1)
        self.assertEqual(focus_blocks[0][0].hour, 9)
        self.assertEqual(focus_blocks[0][1].hour, 17)

    def test_suggest_focus_blocks_with_meetings(self):
        event1 = Event("1", "Meeting A", None, datetime(2025, 6, 11, 9, 0), datetime(2025, 6, 11, 10, 0), None, None, [], False)
        event2 = Event("2", "Meeting B", None, datetime(2025, 6, 11, 11, 0), datetime(2025, 6, 11, 12, 0), None, None, [], False)
        events = [event1, event2]
        from m365_reminder_project.utils import suggest_focus_blocks
        focus_blocks = suggest_focus_blocks(events, start_hour=9, end_hour=17, min_block_duration_minutes=60)
        self.assertEqual(len(focus_blocks), 2)
        self.assertEqual(focus_blocks[0][0].hour, 10)
        self.assertEqual(focus_blocks[0][1].hour, 11)
        self.assertEqual(focus_blocks[1][0].hour, 12)
        self.assertEqual(focus_blocks[1][1].hour, 17)

if __name__ == '__main__':
    unittest.main()


