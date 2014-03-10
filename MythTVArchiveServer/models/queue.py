"""
   :synopsis: Queue Model
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from MythTVArchiveServer.controllers.registry import Base
from MythTVArchiveServer.util.date import mythdate_to_str

class Queue(Base):

    __tablename__ = 'mythtvarchiveserver_queue'
    __table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, program, quality, **kwargs):
        super(Queue, self).__init__(**kwargs)

        self.chan_id = program.chanid
        self.start_time = mythdate_to_str(program.recstartts)
        self.quality = quality
        self.queued = True
        self.created = datetime.now()

        self.info = '%s - %s' % (program.title, program.subtitle)

    id = Column(Integer, primary_key=True)
    chan_id = Column(Integer(10))
    start_time = Column(DateTime)
    queued = Column(Boolean)
    info = Column(String(200))
    message = Column(String(300))
    quality = Column(String(26))
    created = Column(DateTime)
