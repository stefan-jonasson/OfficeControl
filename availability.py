# encoding=utf-8
"""Load meetings for an online calendar"""
from datetime import datetime, timedelta, time
from threading import RLock, Thread
import time as t

import schedule
import requests
from icalendar import Calendar, Event
from pytz import timezone

_TIME_ZONE = timezone('CET')

class AvialabilitySchduler(Thread):
    """Schedules updates to the calendar data"""
    def __init__(self, ical_url):
        super().__init__(daemon=True)
        self._checker = PersonAvailabilityChecker(ical_url)
        self._next_meeting = None
        self._current_meeting = None
        self._lock = RLock()
        self.running = True
        schedule.every().minutes.do(self._update_meetings)
        schedule.every(270).seconds.do(self._update_ical)

    def stop(self):
        """Stop the scheduler"""
        self.running = False

    def run(self):
        """The thread that actually updates things"""
        # Make sure that we do all updates
        self._update_ical()
        self._update_meetings()

        while self.running:
            schedule.run_pending()
            t.sleep(1)

    def _update_meetings(self):
        current_meeting = self._checker.get_current_meeting()
        next_meeting = self._checker.get_next_meeting()
        with (self._lock):
            self._current_meeting = current_meeting
            self._next_meeting = next_meeting

    def get_current_meeting(self):
        """Retrun the current meeting, thread safe"""
        with (self._lock):
            return self._current_meeting

    def get_next_meeting(self):
        """Retrun the next scheduled meeting, thread safe"""
        with (self._lock):
            return self._next_meeting

    def _update_ical(self):
        self._checker.parse_calendar()

class PersonAvailabilityChecker:
    """
    Load a ical file from an url and checks if the person is booked in a metting at the current time
    """
    def __init__(self, ical_url):
        self.ical_url = ical_url
        self._gcal = None
        self._last_updated = None
        self._lock = RLock()

    def parse_calendar(self):
        """Parse the calendar"""
        try:
            print("Updating calendar for {}".format(self.ical_url))
            response = requests.get(self.ical_url)
            gcal = Calendar.from_ical(response.content)
            response.close()
            with (self._lock):
                self._gcal = gcal

            print("Done! Updating calendar for {}".format(self.ical_url))
        except (requests.RequestException, ValueError) as inst:
            print("Could not update calendar {} error: {}".format(self.ical_url, inst))

    def get_current_meeting(self):
        """get the current meeting"""
        return self._get_current_meeting(datetime.now(_TIME_ZONE))

    def get_next_meeting(self):
        """get the next meeting"""
        return self._get_next_meeting(datetime.now(_TIME_ZONE))

    def _get_current_meeting(self, check_time):
        """get the current meeting"""
        if self._gcal is not None:
            with (self._lock):
                for component in self._gcal.walk():
                    if component.name == "VEVENT":
                        start = component.get('dtstart').dt
                        end = component.get('dtend').dt
                        # Convert all to datetime
                        if not isinstance(start, datetime):
                            start = datetime.combine(start, time(tzinfo=_TIME_ZONE))
                        if not isinstance(end, datetime):
                            end = datetime.combine(end, time(23, 59, tzinfo=_TIME_ZONE))

                        if (start < check_time and end > check_time):
                            return Meeting(component)
                        elif start > check_time:
                            break
        return Meeting(None)

    def _get_next_meeting(self, check_time):
        """get the current meeting"""
        if self._gcal is not None:
            for component in self._gcal.walk():
                if component.name == "VEVENT":
                    start = component.get('dtstart').dt
                    # Convert all to datetime
                    if not isinstance(start, datetime):
                        start = datetime.combine(start, time(tzinfo=_TIME_ZONE))
                    if start.date() > check_time.date():
                        break
                    if start > check_time:
                        return Meeting(component)
        return None

    def update(self):
        """Reload the calendar from server when enough time as passed"""
        if (self._last_updated is None or
                (datetime.now(_TIME_ZONE) - self._last_updated).total_seconds() > 600):
            self._last_updated = datetime.now(_TIME_ZONE)
            self.parse_calendar()


class Meeting():
    """Extracts information from a icalendar meeting component"""

    def __init__(self, event: Event):
        self.event = event

    def is_available(self):
        """Return true if user is available"""
        return self.event is None

    def get_location(self):
        """Return the current location or empty"""
        if self.event is not None:
            location = self.event.decoded('location')
            if location is not None:
                location = location.decode("utf-8", "ignore")
                location.replace("_", " ").replace("Konf ", "Konferensrum ")
                return location
        return ""

    def get_summary(self):
        """Return the current meeting"""
        if self.event is not None:
            summary = self.event.decoded('summary')
            if summary is not None:
                return summary.decode("utf-8", "ignore")
        return ""

    def get_start_time(self):
        """Return the current meeting"""
        if self.event is not None:
            return _get_time_as_text(self.event.get('dtstart').dt)
        return ""

    def get_end_time(self):
        """Return the current meeting"""
        if self.event is not None:
            return _get_time_as_text(self.event.get('dtend').dt)
        return ""

    def get_mimutes_to_start(self):
        """Return the current meeting"""
        if self.event is not None:
            return round((self.event.get('dtstart').dt -
                          datetime.now(_TIME_ZONE)).total_seconds() / 60)
        return None


def get_availablilty_message(meeting: Meeting, name: str):
    """ Get the message"""
    if meeting is None or meeting.is_available():
        return "{} har inget möte bokat".format(name)

    summary = meeting.get_summary()
    location = meeting.get_location()

    if not summary:
        return "{} är upptagen, okänd bokning".format(name)

    if not location:
        return "{} är upptagen med {}".format(name, summary)

    return "{} är upptagen med {} i {}".format(name, summary, location)


def _get_time_as_text(event_time: datetime):
    """Converts a datetime object to a string"""
    if event_time is not None:
        if isinstance(event_time, datetime):
            return event_time.strftime("%H:%M")
        # Full day events can span multiple days (Right now we ignore normal multidate meetings)
        if event_time > (datetime.today() + timedelta(days=2)).date():
            return event_time.strftime("%Y-%m-%d")
        if event_time > (datetime.today() + timedelta(days=1)).date():
            return "I övermorgon"
        return "I morgon"
    return ""
