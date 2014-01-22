"""
   :synopsis: Recordings
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from dateutil import parser
from MythTV import Recorded
from MySQLdb.connections import OperationalError

from MythTVArchiveServer.controllers.registry import site_registry

class Recordings(object):
    """
    Used to Access recordings in MythTV.
    """
    def __init__(self):
        self.log = site_registry().log
        self.config = site_registry().config
        self.be = site_registry().mythbe
        self.db = site_registry().mythdb

    def get_recording(self, chan_id, start_time):
        try:
            start_timef = parser.parse(start_time)
            recording = self.be.getRecording(chan_id, start_timef)
            return recording
        except Exception:
            pass

    def recorded_from_program(self, program, recursive=False):
        try:
            return Recorded((program.chanid, program.recstartts), self.db)
        except OperationalError, e:
            if recursive is False:
                if site_registry().mysql_gone_away(e):
                    return self.recorded_from_program(program, recursive=True)
            raise

    def get_recordings(self):
        try:
            recordings = self.be.getRecordings()
            reversed_ = reversed([r for r in recordings])
            return [r for r in reversed_]
        except Exception:
            return []



