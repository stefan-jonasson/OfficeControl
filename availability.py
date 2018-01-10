# encoding=utf-8
"""Load meetings for an online calendar"""
from datetime import datetime, timedelta

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
        """get the current meeting"""
        now = datetime.now(timezone('CET'))

        for component in self.gcal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                if isinstance(start, datetime) and isinstance(end, datetime):
                    if (start < now and end > now):
                        return Meeting(component)
                    elif start > now:
                        break
                else:
                    if (start < now.date() and end > now.date()):
                        return Meeting(component)
                    elif start > now.date():
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
                (datetime.now(timezone('CET')) - self.last_updated).total_seconds() > 600):
            self.last_updated = datetime.now(timezone('CET'))
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
            return self.event.decoded('location').decode("utf-8", "ignore")

        return ""

    def get_summary(self):
        """Return the current meeting"""
        if self.event is not None:
            return self.event.decoded('summary').decode("utf-8", "ignore")

        return ""

    def get_duration(self):
        """Return the current meeting"""
        if self.event is not None:
            event_time = self.event.get('dtend').dt
            if isinstance(event_time, datetime):
                return event_time.time
            else:
                if (event_time > (datetime.today() + timedelta(days=2)).date()):
                    return "I övermorgon"
                else:
                    return "I morgon"
        return ""
