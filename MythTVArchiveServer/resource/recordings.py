"""
   :synopsis: Recordings Resource
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from MythTV import Recorded

from MythTVArchiveServer.lib.recordedshows import Recordings
from MythTVArchiveServer.util.webhelper import build_paginate_links, default_template, process_archive,\
                                               build_archive_link, build_delete_link, process_delete
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.resource.base import BaseDB
from MythTVArchiveServer.models.queue import Queue
from MythTVArchiveServer.util.date import mythdate_to_str

class RecordingsResource(BaseDB):
    """
    Used to display the MythTV recordings.
    """
    def get_queue(self, session, program):

        start_time_to_utc = mythdate_to_str(program.starttime)
        queue = session.query(Queue)\
                    .filter(Queue.chan_id==program.chanid, Queue.start_time==start_time_to_utc)\
                    .order_by(Queue.created.desc())\
                    .limit(1).all()
        if not queue:
            rec = Recorded.fromProgram(program)
            if rec:
                if rec.cutlist == 1:
                    return 'Ready'
            return 'n/a'
        else:
            queue_ = queue[0]
            if queue_.queued is True:
                return 'Queued'
            for status in reversed(queue_.status):
               return status.status

    def custom_render(self, request):

        quality = 'Universal'
        page = request.args.get('page', [0])[0]
        page, paginate_links = build_paginate_links(page, 'recordings')
        rows = 15

        server_url = 'http://localhost:%s' % site_registry().config.server_port
        archive_response = process_archive(server_url, request)
        delete_response = process_delete(request)

        recording_list = Recordings().get_recordings()

        session = site_registry().session


        chunks = []
        start = rows * page
        for i in range(start, start+rows+1):
            try:
                program = recording_list[i]
            except IndexError:
                break

            chunks.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                          % (program.title, program.subtitle if program.subtitle else '',
                             program.season, program.episode, program.inetref, program.category, program.storagegroup,
                             program.description[0:80] if program.description else ''))
            archive_link = build_archive_link(program.chanid, str(program.starttime.utcisoformat()),
                                              quality, 'recordings')
            delete_link = build_delete_link(program.chanid, str(program.recstartts.utcisoformat()), 'recordings')
            queue_status = self.get_queue(session, program)
            chunks.append('<td>%s</td><td>%s</td><td>%s</td><tr>\n' % (queue_status, archive_link, delete_link))

        content = '''
        %s%s
        <table>
        <tr>
        <td>
        %s
        <a href="recordings">Refresh</a>
        </td>
        </tr>
        </table>
        <table class="gridtable">
        <tr>
        <th>Title</th><th>SubTitle</th><th>Sea.</th><th>Ep.</th><th>Ref</th><th>Category</th><th>Storage</th>
        <th>Description</th><th>Status</th><th></th><th></th>
        </tr>
        %s
        </table>
        ''' % (archive_response, delete_response, paginate_links, ''.join(chunks))

        return default_template(content)