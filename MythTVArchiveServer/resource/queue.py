"""
   :synopsis: Queue Resource
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from datetime import datetime

from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.models.queue import Queue
from MythTVArchiveServer.util.webhelper import build_archive_link, build_paginate_links, default_template,\
                                               process_archive, build_delete_link, process_delete, default_params
from MythTVArchiveServer.resource.base import BaseDB

class QueueResource(BaseDB):
    """
    Used to display the queue.
    """
    def custom_render(self, request):

        _default_params = default_params(['page'], request.args)

        page = request.args.get('page', [0])[0]
        page, paginate_links = build_paginate_links(page, 'queue')
        rows = 15

        session = site_registry().session
        session.expire_all()

        server_url = 'http://localhost:%s' % site_registry().config.server_port
        retry_response = process_archive(server_url, request)
        delete_response = process_delete(request, self.recordings.get_recording)

        queues = session.query(Queue)\
                    .order_by(Queue.created.desc())\
                    .offset(page*rows)\
                    .limit(rows).all()
        chunks = []
        for queue in queues:
            chunks.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                          % (queue.info, queue.created, queue.quality, queue.message))
            starttime = endtime = runtime = status_msg = None
            row_css = retry_link = delete_link = ''
            for status in queue.status:
                if status.status == 'running':
                    starttime = status.created
                elif status.status == 'finished':
                    endtime = status.created
                elif status.status == 'error':
                    # Job Errored
                    status_msg = 'Error: %s' % status.message
                    row_css = ' style="background-color: #FFB2B2"'
                    retry_link = build_archive_link(queue.chan_id, queue.start_time, queue.quality, 'queue',
                                                    _default_params)

                if starttime and endtime:
                    # Job Finished Successfully
                    runtime = endtime - starttime
                    status_msg = 'Job Time: %s' % runtime
                    row_css = ' style="background-color: #D4FFA9"'
                    retry_link = build_archive_link(queue.chan_id, queue.start_time, queue.quality, 'queue',
                                                    _default_params)
                    delete_link = build_delete_link(queue.chan_id, queue.start_time, 'recordings', _default_params)

            if status_msg is None and starttime is None:
                # Hasn't Started Yet
                status_msg = 'Queued'
                row_css = ' style="background-color: #FFFF85"'
            elif status_msg is None:
                # Job is Running
                runtime = datetime.now() - starttime
                status_msg = 'Job Running for: %s' % runtime
                row_css = ' style="background-color: #E7F0FF"'

            chunks.append('<td%s>%s</td><td>%s</td><td>%s</td><tr>\n' % (row_css, status_msg, retry_link, delete_link))

        content = '''
        %s
        <table>
        <tr>
        <td>
        %s%s
        <a href="queue">Refresh</a>
        </td>
        </tr>
        </table>
        <table class="gridtable">
        <tr>
        <th>Title</th><th>Created</th><th>Quality</th><th>Message</th><th>Status</th><th></th><th></th>
        </tr>
        %s
        </tr>
        </table>
        ''' % (retry_response, delete_response, paginate_links, ''.join(chunks))

        return default_template(content)