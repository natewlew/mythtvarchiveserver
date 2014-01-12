"""
   :synopsis: Recordings
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from MythTV import MythBE
from dateutil import parser

from MythTVArchiveServer.controllers.registry import site_registry

class Recordings(object):
    """
    Used to Access recordings in MythTV.
    """
    def __init__(self):
        self.log = site_registry().log
        self.config = site_registry().config
        self.be = MythBE()

    def get_recording(self, chan_id, start_time):
        try:
            start_timef = parser.parse(start_time)
            recording = self.be.getRecording(chan_id, start_timef)
            return recording
        except Exception:
            pass

    def get_recordings(self):
        try:
            recordings = self.be.getRecordings()
            reversed_ = reversed([r for r in recordings])
            return [r for r in reversed_]
        except Exception:
            return []



