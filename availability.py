# encoding=utf-8
"""Load meetings for an online calendar"""
from datetime import datetime, timedelta, time

import requests
from icalendar import Calendar, Event
from pytz import timezone


class PersonAvailabilityChecker:
    """
    Load a ical file from an url and checks if the person is booked in a metting at the current time
    """
    def __init__(self, name, ical_url):
        self.name = name
        self.ical_url = ical_url
        self.gcal = None
        self.last_updated = None
        self.last_metting_checked = None
        self.last_meeting_result = None
        self._tzinfo = timezone('CET')
        self.update()

    def parse_calendar(self):
        """Parse the calendar"""
        try:
            print("Updating calendar for {}".format(self.name))
            response = requests.get(self.ical_url)
            self.gcal = Calendar.from_ical(response.content)
            response.close()
            print("Done! Updating calendar for {}".format(self.name))
        except (requests.RequestException, ValueError) as inst:
            print("Could not update calendar {} error: {}".format(self.ical_url, inst))

    def get_current_meeting(self):
        """get the current meeting, only look for new values every new minute"""
        now = datetime.now(self._tzinfo)
        if (self.last_metting_checked is None or
                now.minute != self.last_metting_checked.minute):
            print ("Checking meeting..")
            self.last_meeting_result = self.__get_current_meeting(now)
            self.last_metting_checked = now
        return self.last_meeting_result

    def __get_current_meeting(self, check_time):
        """get the current meeting"""
        if self.gcal is not None:
            for component in self.gcal.walk():
                if component.name == "VEVENT":
                    start = component.get('dtstart').dt
                    end = component.get('dtend').dt
                    # Convert all to datetime
                    if not isinstance(start, datetime):
                        start = datetime.combine(start, time(tzinfo=self._tzinfo))
                    if not isinstance(end, datetime):
                        end = datetime.combine(end, time(23, 59, tzinfo=self._tzinfo))

                    if (start < check_time and end > check_time):
                        return Meeting(component)
                    elif start > check_time:
                        break
        return Meeting(None)

    def get_availablilty_message(self):
        """ Get the message"""
        meeting = self.get_current_meeting()
        if meeting.is_available():
            return "{} har inget möte bokat".format(self.name)

        summary = meeting.get_summary()
        location = meeting.get_location()

        if not summary:
            return "{} är upptagen, okänd bokning".format(self.name)

        if not location:
            return "{} är upptagen med {}".format(self.name, summary)

        return "{} är upptagen med {} i {}".format(self.name, summary, location)


    def update(self):
        """Reload the calendar from server when enough time as passed"""
        if (self.last_updated is None or
                (datetime.now(self._tzinfo) - self.last_updated).total_seconds() > 600):
            self.last_updated = datetime.now(self._tzinfo)
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
                return location.decode("utf-8", "ignore")
        return ""

    def get_summary(self):
        """Return the current meeting"""
        if self.event is not None:
            summary = self.event.decoded('summary')
            if summary is not None:
                return summary.decode("utf-8", "ignore")
        return ""

    def get_duration(self):
        """Return the current meeting"""
        if self.event is not None:
            event_time = self.event.get('dtend').dt
            if isinstance(event_time, datetime):
                return event_time.strftime("%H:%M")
            # Full day events can span multiple days (Right now we ignore normal multidate meetings)
            if event_time > (datetime.today() + timedelta(days=2)).date():
                return event_time.strftime("%Y-%m-%d")
            if event_time > (datetime.today() + timedelta(days=1)).date():
                return "I övermorgon"
            return "I morgon"
        return ""
