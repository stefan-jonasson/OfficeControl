"""Keeps a counter that resets every day"""
from datetime import datetime
from pytz import timezone

class KeyPressCounter:
    """Keeps track of number of keypresses"""
    def __init__(self):
        self.date = datetime.now(timezone('CET')).date()
        self.num = 0

    def update(self):
        """Resets the counter when we enter a new date"""
        if self.date != datetime.now(timezone('CET')).date():
            self.num = 0

    def get_count(self):
        """Return the current count"""
        return self.num

    def increment(self):
        """Increase the counter"""
        self.num += 1
