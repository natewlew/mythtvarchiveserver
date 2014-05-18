"""
   :synopsis: Archive Controller
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

import time, logging
from twisted.internet import defer
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from socket import gethostname

from MythTVArchiveServer.lib.recordedshows import Recordings
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.lib.transcode import Transcode
from MythTVArchiveServer.lib.exportvideo import ExportVideo, ExportType
from MythTVArchiveServer.lib.exceptions import ArchiveError
from MythTVArchiveServer.util.file import remove_file


class ArchiveController(object):

    current_queue = None
    current_message = ''
    record_loop_time = 5

    def __init__(self):
        self.recordings = Recordings()
        self.transcode = Transcode()
        self.log = site_registry().log
        self.session = site_registry().session
        self.config = site_registry().config
        self.record_loop = LoopingCall(self.check_message)
        self.record_loop.start(self.record_loop_time, now=False)

        self.working_files = []

    def recorder(self, msg):
        """ Recorder
        Sets the current log message.
        @param: msg: String
        """
        self.current_message = msg

    def check_message(self):
        """ Check Message
         Check and Update the current message.
        """
        if self.current_message != '':
            self.current_queue.message = self.current_message
            self.log.info(self.current_message)
            self.current_message = ''
            self.session.commit()

    @defer.inlineCallbacks
    def process(self, queue, program):
        """ Process
        Process the next queued program.
        @param: queue: Queue: Database Queue Model
        @param: program: Program: MythTV Program
        """
        self.current_queue = queue
        self.working_files = []

        remote_file = True if program.hostname != gethostname() else False
        if remote_file:
            try:
                if program.hostname != gethostname():
                    yield deferToThread(self.download_recording, program)
            except Exception, e:
                raise ArchiveError('Error Downloading Recording: %r' % e)

        try:
            if remote_file:
                mpg_file = self.get_working_file(program.filename)
            else:
                mpg_file = program.filename

            rec = self.recordings.recorded_from_program(program)

            self.working_files.append(mpg_file)
            self.working_files.append('%s.tmp' % mpg_file)
            self.working_files.append('%s.tmp.map' % mpg_file)
            if mpg_file.endswith('.nuv'):
                self.log.info('Not attempting to cut commercials on a nuv file')
            else:
                if rec.cutlist == 1:
                    yield self.transcode.cut_commercials(mpg_file, self.recorder)
                else:
                    self.log.info('Not cutting commercials, no cutlist.')
        except Exception, e:
            raise ArchiveError('Error cutting commercials: %r' % e)

        tmp_handbrake_file_name = '%s.m4v' % program.filename.split('.')[0]
        tmp_handbrake_file_path = '%s/%s' % (self.config.working_directory, tmp_handbrake_file_name)

        self.working_files.append(tmp_handbrake_file_path)
        try:
            yield self.transcode.handbrake_transcode(mpg_file, tmp_handbrake_file_path,
                                                    queue.quality, self.recorder)
            self.log.info('Handbrake finished')
        except Exception, e:
            raise ArchiveError('Error handbrake transcode: %r' % e)

        try:
            yield deferToThread(self.create_video, tmp_handbrake_file_path, rec, site_registry().mythdb)
        except Exception, e:
            logging.exception(e)
            raise ArchiveError('Create Video Error: %r' % e)

        try:
            self.cleanup()
        except Exception, e:
            raise ArchiveError('Error cleaning up file: %r' % e)

        try:
            if self.config.delete_recording_on_finish:
                program.delete()
        except Exception, e:
            raise ArchiveError('Attempt to Delete Recording: %r' % e)

    def download_recording(self, program):
        """ Download Recording
        Download recording from the mythtv backend server.
        @param: program: Program: MythTV Program
        """
        self.log.debug('Downloading File from Backend Server')
        stime = time.time()
        htime = [stime,stime,stime,stime]
        srcsize = program.filesize
        file_ = '%s/%s' % (self.config.working_directory, program.filename)
        try:
            srcfp = program.open()
            dstfp = open(file_, 'wb')

            tsize = 2**24
            while tsize == 2**24:
                tsize = min(tsize, srcsize - dstfp.tell())
                dstfp.write(srcfp.read(tsize))
                htime.append(time.time())
                rate = float(tsize*4)/(time.time()-htime.pop(0))
                remt = (srcsize-dstfp.tell())/rate
                self.recorder("Download %02d%% complete - %d seconds remaining" %\
                                (dstfp.tell()*100/srcsize, remt))
            srcfp.close()
            dstfp.close()
        except Exception:
            raise

    def get_working_file(self, file_name):
        """ Get Working File
        @param: file_name: String
        """
        working_dir = self.config.working_directory
        working_file = '%s/%s' % (working_dir, file_name)
        return working_file

    def create_video(self, file_, recorded, db):
        """ Create Video
        Create the final archive video.
        @param: file_: String:
        @param: recorded: Recorded: MythTV Recorded
        """
        export_type = self.config.export_type
        ExportType.validate(export_type)
        ExportVideo(file_, recorded, self.recorder, db, export_type)

    @defer.inlineCallbacks
    def cleanup(self):
        """ Cleanup
        Cleanup the working files when finished.
        """
        if self.working_files:
            yield deferToThread(self._cleanup, self.working_files)
            self.working_files = []

    def _cleanup(self, files):
        error = None
        for file_ in files:
            try:
                remove_file(file_)
            except Exception, e:
                error = e
        if error:
            raise error
