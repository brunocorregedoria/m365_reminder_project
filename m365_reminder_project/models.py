import os
from datetime import datetime, timedelta, timezone


class User:
    def __init__(self, id, display_name, email):
        self.id = id
        self.display_name = display_name
        self.email = email


class Event:
    def __init__(
        self,
        id,
        subject,
        body_preview,
        start_datetime,
        end_datetime,
        location,
        organizer,
        attendees,
        is_all_day,
    ):
        self.id = id
        self.subject = subject
        self.body_preview = body_preview
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.location = location
        self.organizer = organizer
        self.attendees = attendees
        self.is_all_day = is_all_day

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "bodyPreview": self.body_preview,
            "start": {"dateTime": self.start_datetime.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": self.end_datetime.isoformat(), "timeZone": "UTC"},
            "location": {"displayName": self.location} if self.location else None,
            "organizer": (
                {
                    "emailAddress": {
                        "name": self.organizer.get("name"),
                        "address": self.organizer.get("address"),
                    }
                }
                if self.organizer
                else None
            ),
            "attendees": self.attendees,
            "isAllDay": self.is_all_day,
        }

    @classmethod
    def from_dict(cls, event_dict):
        start_dt = datetime.fromisoformat(
            event_dict["start"]["dateTime"].replace("Z", "+00:00")
        )
        end_dt = datetime.fromisoformat(
            event_dict["end"]["dateTime"].replace("Z", "+00:00")
        )
        location = event_dict.get("location", {}).get("displayName")
        organizer = event_dict.get("organizer", {}).get("emailAddress")
        attendees = event_dict.get("attendees", [])
        is_all_day = event_dict.get("isAllDay", False)
        return cls(
            event_dict["id"],
            event_dict["subject"],
            event_dict.get("bodyPreview"),
            start_dt,
            end_dt,
            location,
            organizer,
            attendees,
            is_all_day,
        )
