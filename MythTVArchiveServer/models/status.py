"""
   :synopsis: Status Model
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from MythTVArchiveServer.controllers.registry import Base
from MythTVArchiveServer.models.queue import Queue

class StatusType(object):
    running = 'running'
    finished = 'finished'
    error = 'error'


class Status(Base):

    __tablename__ = 'mythtvarchiveserver_status'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    status = Column(String(12))
    message = Column(String(300))
    created = Column(DateTime)

    queue_id = Column(Integer, ForeignKey(Queue.id))

    queue = relationship(Queue, backref='status')
