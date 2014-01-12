"""
   :synopsis: Logger
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from MythTV import MythLog, MythDB

class Log(object):
    """
    Used to Log to MythTV Database.
    """
    def __init__(self):

        self.db = MythDB()
        self.log = MythLog(module='mythtvarchiveserver', db=self.db)
        self.default_log_mask = MythLog.GENERAL

    def debug(self, msg):
        self.log(self.default_log_mask, MythLog.DEBUG, msg)

    def info(self, msg):
        self.log(self.default_log_mask, MythLog.INFO, msg)

    def warning(self, msg):
        self.log(self.default_log_mask, MythLog.WARNING, msg)

    def error(self, msg):
        self.log(self.default_log_mask, MythLog.ERR, msg)

    def critical(self, msg):
        self.log(self.default_log_mask, MythLog.CRIT, msg)
