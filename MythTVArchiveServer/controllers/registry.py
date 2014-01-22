"""
   :synopsis: Registry Controller
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DisconnectionError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import Pool
from twisted.internet import reactor

from MythTV import MythBE, MythDB

_site_registry = None
Base = declarative_base()

def site_registry():
    """
    Global Access to the Registry Controller.
    """
    return _site_registry

from MythTVArchiveServer.controllers.config import ConfigController
from MythTVArchiveServer.controllers.queue import QueueController
from MythTVArchiveServer.controllers.archive import ArchiveController
from MythTVArchiveServer.util.logger import Log


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise DisconnectionError()
    cursor.close()

class RegistryController(object):
    """
    Registry Controller is loaded first and is a single place to access
    common objects in the application.
    """

    def __init__(self, skip_controllers=False):

        self._config = ConfigController()

        db_args = self._config.db_args

        self._mythdb = MythDB(args=db_args)
        self._mythbe = MythBE(db=self._mythdb)

        self._log = Log(self._mythdb)

        self._base = None
        self._session = None
        self.init_session()

        if self._config.init_db:
            self._base.metadata.create_all()
            self._config.init_db = False

        self._archive = None
        self._queue = None

        if skip_controllers is True:
            self.close_session()
        else:
           reactor.callLater(1, self._init_controllers)

    def _init_controllers(self):
        self.log.info('Init Controllers')
        self._archive = ArchiveController()
        self._queue = QueueController()

    def init_session(self):
        if self._session is None:
            engine = create_engine(self._config.db_dsn, isolation_level="READ UNCOMMITTED")
            self._base = Base
            self._base.metadata.bind = engine
            Session = sessionmaker(bind=engine)
            self._session = Session()

    def close_session(self):
        if not self._session is None:
            self._session.close()
            self._session = None

    @property
    def log(self):
        return self._log

    @property
    def config(self):
        return self._config

    @property
    def base(self):
        return self._base
    @property
    def session(self):
        return self._session

    @property
    def mythbe(self):
        return self._mythbe

    @property
    def mythdb(self):
        return self._mythdb

    @property
    def queue(self):
        return self._queue

    @property
    def archive(self):
        return self._archive

    def mysql_gone_away(self, e):
        try:
            if e.args[0] == 2006:
                self._mythdb.db.__del__()
                self._mythdb.db._pool = []
                self._mythdb.db._inuse = []
                return True
        except (IndexError, AttributeError):
            pass
        return False


skip_controllers_ = os.environ.get('SKIP_CONTROLLERS', 'False') == 'True'
_site_registry = RegistryController(skip_controllers=skip_controllers_)

