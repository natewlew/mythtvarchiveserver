"""
   :synopsis: ExportVideo
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

import time, os
from re import sub
from shutil import move

from MythTV import Video, VideoGrabber, MythError
from MythTVArchiveServer.lib.exceptions import ArchiveError
from MythTVArchiveServer.controllers.registry import site_registry


class ExportType(object):
    file_ = 'file'
    mythvideo = 'mythvideo'

    @staticmethod
    def validate(export_type):
        if not export_type in [ExportType.file_, ExportType.mythvideo]:
            raise ArchiveError('Invalid Export Type: %r' % export_type)


class VideoStub(object):
    hostname = ''
    filename = ''

    def delete(self):
        pass

    def importMetadata(self, value):
        pass


class ExportVideo(object):
    """
    Used to Export transcoded video into MythTV Video or a directory.

    Note: Export to MythTV Video only works if the MythTV install is
        local or the storage group drive path is mapped correctly on
        the local machine. The transfer to mythtv will appear to work
        but the file will be broken if mythprotocol is used. Would
        like to fix this.

    Lots of code in this file was copied from:
        https://github.com/wagnerrp/mythtv-scripts/blob/master/python/mythvidexport.py
    This file would not have been possible without it.
    """

    def __init__(self, file_, recorded, recorder, db, export_type=ExportType.mythvideo):
        self.file_ = file_
        self.db = db
        self.recorder = recorder
        self.config = site_registry().config

        if export_type == ExportType.mythvideo:
            self.vid = Video(db=self.db).create({'title': '', 'filename': '', 'host': self.config.export_hostname})
        elif export_type == ExportType.file_:
            self.vid = VideoStub()
        else:
            raise ArchiveError('Invalid Export Type: %r' % export_type)

        self.rec = recorded

        self.log = site_registry().log

        ###############
        ## Set Formats

        self.ext = 'm4v'
        self.type = 'TV'

        # TV Format
        self.tfmt = 'Television/%TITLE%/Season_%SEASON%/'+\
                        '%TITLE%-S%SEASON%E%EPISODEPAD%-%SUBTITLE%'
        # Movie Format
        self.mfmt = 'Movies/%TITLE%'
        # Generic Format
        self.gfmt = 'Videos/%TITLE%'

        self.get_metadata()
        self.get_destination()

        if export_type == ExportType.mythvideo:
            self.copy()
            self.vid.update()
        elif export_type == ExportType.file_:
            self.write_file()

    def copy(self):
        """ Copy
        Copy the video into MythTV Video.
        """
        try:
            self.log.debug('Uploading final Transcoded File')
            stime = time.time()
            htime = [stime,stime,stime,stime]

            srcfp = open(self.file_, 'r')
            srcsize = int(os.fstat(srcfp.fileno()).st_size)
            dstfp = self.vid.open('w', nooverwrite=False)

            tsize = 2**24
            while tsize == 2**24:
                tsize = min(tsize, srcsize - dstfp.tell())
                dstfp.write(srcfp.read(tsize))
                htime.append(time.time())
                rate = float(tsize*4)/(time.time()-htime.pop(0))
                remt = (srcsize-dstfp.tell())/rate
                self.recorder("Video %02d%% complete - %d seconds remaining" %\
                                (dstfp.tell()*100/srcsize, remt))

            srcfp.close()
            dstfp.close()

            self.vid.hash = self.vid.getHash()

        except Exception, e:
            raise ArchiveError('Create Video Error: %r' % e)

    def get_metadata(self):
        """ Get Metadata
        Get the recording metadata.
        """
        self.vid.hostname = self.db.gethostname()
        try:
            if self.rec.inetref:
                # good data is available, use it
                if self.rec.season > 0 or self.rec.episode > 0:
                    self.type = 'TV'
                    grab = VideoGrabber(self.type)
                    metadata = grab.grabInetref(self.rec.inetref, self.rec.season, self.rec.episode)
                else:
                    self.type = 'MOVIE'
                    grab = VideoGrabber(self.type)
                    metadata = grab.grabInetref(self.rec.inetref)
            else:
                if self.rec.subtitle:
                    # subtitle exists, assume tv show
                    self.type = 'TV'
                    grab = VideoGrabber(self.type)
                    match = grab.sortedSearch(self.rec.title, self.rec.subtitle)
                else: # assume movie
                    self.type = 'MOVIE'
                    grab = VideoGrabber(self.type)
                    match = grab.sortedSearch(self.rec.title)

                if len(match) == 0:
                    # no match found
                    metadata = self.rec.exportMetadata()
                elif (len(match) > 1) & (match[0].levenshtein > 0):
                    # multiple matches found, and closest is not exact
                    self.vid.delete()
                    raise ArchiveError('Multiple metadata matches found: '\
                                                       +self.rec.title)
                else:
                    metadata = grab.grabInetref(match[0])
        except (MythError, StopIteration), e:
            self.log.warning('Error Getting Metadata: %r' % e)
            metadata = self.rec.exportMetadata()

        self.vid.importMetadata(metadata)

    def get_destination(self):
        """ Get Destination
        Get destination path.
        """
        if self.type == 'TV':
            self.vid.filename = self.process_format(self.tfmt)
        elif self.type == 'MOVIE':
            self.vid.filename = self.process_format(self.mfmt)
        elif self.type == 'GENERIC':
            self.vid.filename = self.process_format(self.gfmt)

    def process_format(self, fmt):
        """ Process Format
        Process the final path and name.
        """
        rep = ( ('%TITLE%','title','%s'), ('%SUBTITLE%','subtitle','%s'),
            ('%SEASON%','season','%d'), ('%SEASONPAD%','season','%02d'),
            ('%EPISODE%','episode','%d'), ('%EPISODEPAD%','episode','%02d'),
            ('%YEAR%','year','%s'), ('%DIRECTOR%','director','%s'))
        for tag, data, format in rep:
            if self.vid[data]:
                fmt = fmt.replace(tag,format % self.vid[data])
            else:
                fmt = fmt.replace(tag,'')

        # replace fields from program data
        rep = ( ('%HOSTNAME%', 'hostname', '%s'),
                ('%STORAGEGROUP%','storagegroup','%s'))
        for tag, data, format in rep:
            data = getattr(self.rec, data)
            fmt = fmt.replace(tag,format % data)

        if len(self.vid.genre):
            fmt = fmt.replace('%GENRE%',self.vid.genre[0].genre)
        else:
            fmt = fmt.replace('%GENRE%','')

        fmt = fmt.replace(' ', '_')
        fmt = sub('[^0-9a-zA-Z_/-]+', '', fmt)
        return '%s.%s' % (fmt, self.ext)

    def write_file(self):
        """ Write File
        If not exporting to MythTV, write the file to archive directory path.
        """
        archive_dir = self.config.archive_directory
        if archive_dir.endswith('/'):
            archive_dir = archive_dir[:-1]

        filename_dirs = self.vid.filename.split('/')
        filename_dirs.pop() # get rid of the actual filename

        path_check = archive_dir
        for filename_dir in filename_dirs:
            path_check = '%s/%s' % (path_check, filename_dir)
            if not os.path.exists(path_check):
                try:
                    os.makedirs(path_check)
                except OSError:
                    raise ArchiveError('Could Not Create Directory: %s' % path_check)

        final_filename = '%s/%s' % (archive_dir, self.vid.filename)
        try:
            move(self.file_, final_filename)
        except Exception, e:
            raise ArchiveError('Could not move file to: %s' % final_filename)
