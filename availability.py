# encoding=utf-8
from icalendar import Calendar, Event
from datetime import datetime, date
from pytz import UTC, timezone
import urllib2

class PersonAvailabilityChecker:
    """ 
    Load a ical file from an url and checks if the person is booked in a metting at the current time
    """
    def __init__(self, name, icalURL):
        self.name = name
        self.icalURL = icalURL
        self.gcal = None
        #self.parseCalendar()

    def parseCalendar(self):
        response = urllib2.urlopen(self.icalURL)
        self.gcal = Calendar.from_ical(response.read())
        response.close()

    def getCurrentMeeting(self):
        now = datetime.now(timezone('CET'))

        for component in self.gcal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                if (type(start) is date):
                    if (start < now.date() and end > now.date()):
                        return component
                    elif (start > now.date()):
                        break
                elif (type(start) is datetime and type(end) is datetime):
                    if (start < now and end > now):            
                        return component
                    elif (start > now):
                        break
        return None

    def getAvailabliltyMessage(self):
        component = self.getCurrentMeeting()
        if (component is None):
            return "{} är ledig, har inget bokat för tillfället".format(self.name)
        else:
            return "{} är upptagen i möte {}".format(self.name, component.decoded('summary'))


