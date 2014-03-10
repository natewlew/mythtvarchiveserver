"""
   :synopsis: Recordings Resource
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""


from MythTVArchiveServer.util.webhelper import build_paginate_links, default_template, process_archive,\
                                               build_archive_link, build_delete_link, process_delete, build_checkbox, \
                                               default_params
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.resource.base import BaseDB
from MythTVArchiveServer.models.queue import Queue
from MythTVArchiveServer.util.date import mythdate_to_str

class RecordingsResource(BaseDB):
    """
    Used to display the MythTV recordings.
    """

    def get_queue(self, session, program):

        start_time_to_utc = mythdate_to_str(program.recstartts)
        queue = session.query(Queue)\
                    .filter(Queue.chan_id==program.chanid, Queue.start_time==start_time_to_utc)\
                    .order_by(Queue.created.desc())\
                    .limit(1).all()
        if not queue:
            rec = self.recordings.recorded_from_program(program)
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

        _default_params = default_params(['page', 'storage', 'status'], request.args)

        quality = 'Universal'
        page = request.args.get('page', [0])[0]
        page, paginate_links = build_paginate_links(page, 'recordings',
                                                    default_params(['storage', 'status'], request.args))
        rows = 15

        storage = request.args.get('storage', [[]])[0]
        status = request.args.get('status', [[]])[0]

        server_url = 'http://localhost:%s' % site_registry().config.server_port
        archive_response = process_archive(server_url, request)
        delete_response = process_delete(request, self.recordings.get_recording)

        recording_list = self.recordings.get_recordings()

        session = site_registry().session

        prune = []

        if storage:
            for program in recording_list:
                if not program.storagegroup in storage:
                    prune.append(program)

        if status:
            for program in recording_list:
                queue_status = self.get_queue(session, program)
                if not queue_status in status:
                    prune.append(program)
                else:
                    program.queue_status = queue_status

        if prune:
            for program in prune:
                recording_list.remove(program)

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
            archive_link = build_archive_link(program.chanid, str(program.recstartts.utcisoformat()),
                                              quality, 'recordings', _default_params)
            delete_link = build_delete_link(program.chanid, str(program.recstartts.utcisoformat()), 'recordings',
                                            _default_params)

            if status:
                queue_status = program.queue_status
            else:
                queue_status = self.get_queue(session, program)

            chunks.append('<td>%s</td><td>%s</td><td>%s</td><tr>\n' % (queue_status, archive_link, delete_link))

        storage_values = {
            'LiveTV': 'LiveTV',
            'Default': 'Default',
        }
        storage_checkbox = build_checkbox('storage', storage_values, storage)

        status_values = {
            'n/a': 'n/a',
            'Ready': 'ready',
            'Queued': 'queued',
            'finished': 'finished',
            'error': 'error',
        }
        status_checkbox = build_checkbox( 'status', status_values, status)

        content = '''
        %s%s
        <table>
        <tr>
        <td>
        %s
        <a href="recordings">Refresh</a>
        </td>
        <td>
        <form action="recordings">
        <table>
        <tr>
        <td><b>Storage:</b></td><td>%s</td>
        <td><b>Status:</b></td><td>%s</td>
        <td><input type="submit" value="Submit"></td>
        </tr>
        </table>
        <input type="hidden" name="page" value="%d">
        </form>
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
        ''' % (archive_response, delete_response, paginate_links, storage_checkbox, status_checkbox, page,
               ''.join(chunks))

        return default_template(content)