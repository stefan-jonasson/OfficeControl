# encoding=utf-8
from datetime import date, datetime

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
        self.parse_calendar()

    def parse_calendar(self):
        response = requests.get(self.ical_url)
        self.gcal = Calendar.from_ical(response.content)
        response.close()

    def get_current_meeting(self):
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
        component = self.get_current_meeting()
        if component is None:
            return "{} är ledig, har inget bokat för tillfället".format(self.name)

        return "{} är upptagen i möte {}".format(self.name, component.decoded('summary'))
