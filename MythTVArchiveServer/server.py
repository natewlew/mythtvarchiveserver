"""
   :synopsis: Archive Server
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from twisted.web.xmlrpc import XMLRPC
from twisted.web.server import Site
from twisted.internet import reactor

import MythTVArchiveServer.controllers.registry as registry

from MythTVArchiveServer.lib.recordedshows import Recordings
from MythTVArchiveServer.lib.transcode import Quality


registry.init_registry()


class ArchiveServer(XMLRPC):
    """ Archive XMLRPC Server
    Used to add the MythTV recording to the Queue.
    """
    def __init__(self, *args, **kwargs):
        XMLRPC.__init__(self, *args, **kwargs)
        self.recording = Recordings()
        self.log = registry.site_registry().log

    @property
    def queue(self):
        return registry.site_registry().queue

    def _get_return_value(self, message, success):
        return {
            'message': message,
            'success': success
        }

    def _archive(self, chanID, startTime, quality):
        program = self.recording.get_recording(chanID, startTime)
        if program:
            msg = 'Archiving %s. (%s, %s)' % (program.title, chanID, startTime)
            self.log.info(msg)
            result = self._get_return_value(msg, True)
            self.queue.add_to_queue(program, quality)
        else:
            msg = 'Could not find Recording: %r, %r' % (chanID, startTime)
            self.log.info(msg)
            result = self._get_return_value(msg, False)
        return result

    def xmlrpc_archive(self, chanID, startTime, quality):
        """ XMLRPC Archive
        @param: chanID: String: MythTV Channel ID
        @param: startTime: MythTV UTC Start Time
        @param: quality: Handbrake Quality
        """
        if Quality.validate(quality):
            return self._archive(chanID, startTime, quality)
        else:
            msg = 'Invalid Quality: %r' % quality
            self.log.error(msg)
            return self._get_return_value(msg, False)


def twistd_plugin():
    config = registry.site_registry().config
    reactor.listenTCP(config.server_port, Site(ArchiveServer()))
    reactor.run()

if __name__ == '__main__':
    twistd_plugin()