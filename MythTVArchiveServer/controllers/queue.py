"""
   :synopsis: Queue Controller
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

from MythTVArchiveServer.lib.exceptions import ArchiveError
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.models.queue import Queue as QueueModel
from MythTVArchiveServer.models.status import Status, StatusType
from MythTVArchiveServer.lib.recordedshows import Recordings


class QueueController(object):

    def __init__(self):
        self.archive = site_registry().archive
        self.log = site_registry().log
        self.session = site_registry().session
        self.queue_check_loop = LoopingCall(self.queue_check)
        self.recordings = Recordings()
        self.config = site_registry().config

        reactor.callLater(2, self.start_loop)

    def start_loop(self, *args):
        self.queue_check_loop.start(1, now=False)

    def stop_loop(self):
        self.queue_check_loop.stop()

    def lock(self):
        """ Lock
        Lock the queue by stopping the queue check loop.
        """
        self.stop_loop()
        self.log.info('Locking Thread')

    def clear_lock(self, queue_id):
        """ Clear Lock
        Clear the lock by starting the queue check loop.
        """
        self.log.info('Unlocking Thread')
        self.update_status(queue_id, StatusType.finished)
        self.start_loop()

    def record_error(self, queue_id, message):
        """ Record Error
        Record a queue error.
        """
        self.log.error(message)
        self.update_status(queue_id, StatusType.error, message=message)
        self.start_loop()

    @inlineCallbacks
    def queue_check(self):
        """ Queue Check
        Check queue for new recording to archive.
        """
        queue = self.get_next_queue()
        if queue:
            self.lock()
            queue.queued = False
            self.update_status(queue.id, StatusType.running)
            try:
                self.log.info('Processing: %s - %s' % (queue.chan_id, queue.start_time))
                start_time_str = '%sZ' % str(queue.start_time).replace(' ', 'T')
                program = self.recordings.get_recording(queue.chan_id, start_time_str)
                yield self.archive.process(queue, program)
            except ArchiveError, e:
                try:
                    if self.config.cleanup_on_error:
                        self.archive.cleanup()
                except:
                    pass
                self.record_error(queue.id, str(e))
            else:
                self.clear_lock(queue.id)

    def add_to_queue(self, program, quality):
        """ Add to Queue
        Add program to queue.
        @param: program: Program: MythTV Program
        @param: quality: lib.transcode.Quality
        """
        queue = QueueModel(program, quality)
        self.session.add(queue)
        self.session.commit()

    def update_status(self, queue_id, status_type, message=None):
        """ Update Status
        Update the Status of the Archive.
        @param: queue_id: Int
        @param: status_type: models.status.StatusType
        """
        status = Status(queue_id=queue_id, status=status_type, created=datetime.now(), message=message)
        self.session.add(status)
        self.session.commit()

    def get_next_queue(self):
        """ Get next Queue
        Get the next recording the the queue.
        """
        try:
            return self.session.query(QueueModel).filter(QueueModel.queued==True)\
                            .order_by(QueueModel.created.asc()).limit(1).one()
        except NoResultFound:
            pass

