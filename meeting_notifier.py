"""Keeps a counter that resets every day"""
from availability import AvialabilitySchduler
from ttsplay import TextMessagePlayer

class MeetingNotifier:
    """Keeps track of number of keypresses"""
    def __init__(self, name: str,
                 meeting_provider: AvialabilitySchduler,
                 tts_player: TextMessagePlayer):
        self.name = name
        self.tts_player = tts_player
        self.meeting_provider = meeting_provider
        self._minutes_to_next_meeting = None

    def update(self):
        """Play a message every minute until next meeting"""
        next_meeting = self.meeting_provider.get_next_meeting()
        if next_meeting is not None:
            minutes_to_next_meeting = next_meeting.get_mimutes_to_start()
            if self._minutes_to_next_meeting != minutes_to_next_meeting:
                self._minutes_to_next_meeting = minutes_to_next_meeting
                if minutes_to_next_meeting > 0:
                    if minutes_to_next_meeting == 1:
                        self.tts_player.queue_text(
                            "{}, du har ett möte om en minut i {}".format(
                                self.name, next_meeting.get_location()))

                    elif minutes_to_next_meeting < 6:
                        self.tts_player.queue_text(
                            "{}, du har ett möte om {} minuter i {}".format(
                                self.name, minutes_to_next_meeting, next_meeting.get_location()))
