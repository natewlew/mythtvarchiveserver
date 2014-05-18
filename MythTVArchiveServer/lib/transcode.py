"""
   :synopsis: Transcode
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from os import environ
from shutil import move
from twisted.internet import protocol, defer, reactor
from twisted.internet.error import ProcessDone
from twisted.internet.threads import deferToThread

from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.lib.exceptions import ArchiveError


class TranscodeProcess(protocol.ProcessProtocol):

    d = None

    def __init__(self, recorder):
        self.recorder = recorder

    def connectionMade(self):
        self.d = defer.Deferred()

    def outReceived(self, data):
        """
        Some data was received from stdout.
        """
        if self.recorder:
            self.recorder(data)

    def errReceived(self, data):
        """
        Some data was received from stderr.
        """
        if self.recorder:
            self.recorder(data)

    def processEnded(self, reason):
        if reason.check(ProcessDone):
            self.d.callback('Finished')
        else:
            self.d.errback(reason)


class Quality(object):
    """
    Options for Handbrake Presets.
    """
    universal = 'Universal'
    ipod = 'iPod'
    iphone = 'iPhone & iPod touch'
    ipad = 'iPad'
    apple_tv = 'AppleTV'
    apple_tv2 = 'AppleTV 2'
    apple_tv3 = 'AppleTV 3'
    android = 'Android'
    android_tablet = 'Android Tablet'
    normal = 'Normal'
    high_profile = 'High Profile'

    @staticmethod
    def validate(value):
        if value in [Quality.universal, Quality.ipod, Quality.iphone, Quality.ipad, Quality.apple_tv,
                     Quality.apple_tv2, Quality.apple_tv3, Quality.android, Quality.android_tablet,
                     Quality.normal, Quality.high_profile]:
            return True
        else:
            return False


class Transcode(object):
    """
    Used to Trancsode MythTV recording. Uses mythtranscode to remove commercials (if there is
    a cutlist) then Handbrake to make the file smaller.
    """
    mythtranscode = '/usr/bin/mythtranscode'
    handbrake = '/usr/bin/HandBrakeCLI'

    def __init__(self):
        self.log = site_registry().log
        self.config = site_registry().config

    def transcode_process(self, cmd, recorder):
        transcode_process = TranscodeProcess(recorder)
        reactor.spawnProcess(transcode_process, cmd[0], cmd, env=environ)
        return transcode_process.d

    @defer.inlineCallbacks
    def cut_commercials(self, file_, recorder):
        """ Cut Commercials
        Cut commercials from MythTV recording.
        @param: file_: String
        @prams: recorder: Method for logging
        """
        try:
            self.log.info('Calling mythtranscode')
            command = [self.mythtranscode, '-i', file_, '-o', '%s.tmp' % file_, '--mpeg2', '--honorcutlist']
            yield self.transcode_process(command, recorder)
        except Exception, e:
            try:
                allowed_errors = self.config.commercial_cut_allowed_error_codes
                if e.exitCode in allowed_errors:
                    self.log.info('Continuing without cutting commercials')
                else:
                    raise e
            except AttributeError:
                raise e
        else:
            try:
                self.log.debug('Overwriting original file')
                yield self.move('%s.tmp' % file_, file_, recorder)
            except Exception:
                raise

    @defer.inlineCallbacks
    def handbrake_transcode(self, in_file, out_file, quality, recorder):
        """ HandBrake Transcode
        Transcode recording using HandBrake.
        @param: in_file: String
        @param: out_file: String
        @param: quality: Quality
        @prams: recorder: Method for logging
        """
        self.log.info('Starting Handbrake transcode')

        # If the preset has a space, add quotes.
        if quality.find(' ') == -1:
            preset = quality
        else:
            preset = '"%s"' % quality

        command = [self.handbrake, '-i', in_file, '-o', out_file, '--audio', '1', '--aencoder',
                   'copy:aac', '--audio-fallback', 'faac', '--audio-copy-mask', 'aac', '--preset', preset]
        yield self.transcode_process(command, recorder)

    def _move(self, in_file, out_file):
        try:
            move(in_file, out_file)
        except Exception:
            raise ArchiveError('Error Moving File to: %s' % out_file)

    @defer.inlineCallbacks
    def move(self, in_file, out_file, recorder=None):
        self.log.debug('Overwriting original file')
        yield deferToThread(self._move, in_file, out_file)
