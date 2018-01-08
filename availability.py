# encoding=utf-8
"""Load meetings for an online calendar"""
from datetime import datetime

import requests
from icalendar import Calendar
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
        response = requests.get(self.ical_url)
        self.gcal = Calendar.from_ical(response.content)
        response.close()

    def get_current_meeting(self):
        """get the current meeting"""
        now = datetime.now(timezone('CET'))

        for component in self.gcal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                if isinstance(start, datetime) and isinstance(end, datetime):
                    if (start < now and end > now):
                        return component
                    elif start > now:
                        break
                else:
                    if (start < now.date() and end > now.date()):
                        return component
                    elif start > now.date():
                        break
        return None

    def get_availablilty_message(self):
        """ Get the message"""
        component = self.get_current_meeting()
        if component is None:
            return "{} har inget möte bokat".format(self.name)

        if component.decoded('summary', None) is None:
            return "{} är upptagen, okänd bokning".format(self.name)

        summary = component.decoded('summary').decode("utf-8", "ignore")

        if component.decoded('location', None) is None:
            return "{} är upptagen med {}".format(self.name, summary)

        location = component.decoded('location').decode("utf-8", "ignore")

        return "{} är upptagen med {} i {}".format(self.name, summary, location)

    def update(self):
        """Reload the calendar from server when enough time as passed"""
        if (self.last_updated is None or
                (datetime.now(timezone('CET')) - self.last_updated).total_seconds() > 300):
            self.last_updated = datetime.now(timezone('CET'))
            self.parse_calendar()
