"""Keeps a counter that resets every day"""
from datetime import datetime, date
from pytz import timezone

class KeyPressCounter:
    """Keeps track of number of keypresses"""
    def __init__(self, initial_num, stat_date):
        if stat_date is not None and isinstance(stat_date, date):
            self.date = stat_date
        else:
            self.date = datetime.now(timezone('CET')).date()

        if initial_num is not None:
            self.num = initial_num
        else:
            self.num = 0

    def update(self):
        """Resets the counter when we enter a new date"""
        current_date = datetime.now(timezone('CET')).date()
        if self.date != current_date:
            self.num = 0
            self.date = current_date

    def get_count(self):
        """Return the current count"""
        return self.num

    def increment(self):
        """Increase the counter"""
        self.num += 1

    def get_stat_date(self):
        """Returns the current date for statistics"""
        return self.date
