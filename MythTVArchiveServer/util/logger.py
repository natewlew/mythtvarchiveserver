"""
   :synopsis: Logger
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from MythTV import MythLog, MythDB
from MySQLdb.connections import OperationalError

from MythTVArchiveServer.controllers.registry import site_registry


class Log(object):
    """
    Used to Log to MythTV Database.
    """
    def __init__(self, db):

        self.db = db
        self.log = MythLog(module='mythtvarchiveserver', db=self.db)
        self.default_log_mask = MythLog.GENERAL

    def _log(self, level, msg, recursive=False):

        try:
            self.log(self.default_log_mask, level, msg)
        except OperationalError, e:
            if recursive is False:
                if site_registry().mysql_gone_away(e):
                    self._log(level, msg, recursive=True)
                    return
            raise

    def debug(self, msg):
        self._log(MythLog.DEBUG, msg)

    def info(self, msg):
        self._log(MythLog.INFO, msg)

    def warning(self, msg):
        self._log(MythLog.WARNING, msg)

    def error(self, msg):
        self._log(MythLog.ERR, msg)

    def critical(self, msg):
        self._log(MythLog.CRIT, msg)
