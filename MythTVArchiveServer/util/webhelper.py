"""
   :synopsis: Web Helper
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from MythTVArchiveServer.util.clienthelper import archive_recording

def process_archive(server_url, request):
    """ Process Archive
    Process an archive request.
    @param: server_url: String
    @param: request: Twisted Resource Request
    """
    try:
        archive = int(request.args.get('archive', [''])[0])
        chan_id = int(request.args.get('chan_id', [''])[0])
        start_time = request.args.get('start_time', [''])[0]
        quality = request.args.get('quality', [''])[0]
        return archive_recording(server_url, chan_id, start_time, quality)
    except (ValueError, TypeError):
        return ''

def process_delete(request, get_recording_method):
    """ Process Delete
    Process a delete request.
    @param: request: Twisted Resource Request
    """
    try:
        delete = int(request.args.get('delete', [''])[0])
        chan_id = int(request.args.get('chan_id', [''])[0])
        start_time = request.args.get('start_time', [''])[0]
        program = get_recording_method(chan_id, start_time)
        if program:
            result = program.delete()
            if result == -1:
                result = 'Program was successfully deleted'
            else:
                result = 'Could not delete program: %r' % result
        else:
            result = 'Could Not Find Program'
        return result
    except (ValueError, TypeError):
        return ''

def build_archive_link(chan_id, start_time, quality, url):
    """ Build Archive Link
    @param: chan_id: String: Channel ID
    @param: start_time: String: Program Start Time
    @param: quality: Quality
    @param: url: String
    """
    start_time_str = '%sZ' % str(start_time).replace(' ', 'T')
    on_click = 'onclick="return confirm(\'Are you sure want to Archive this MythTV Recording?\');"'
    return '<a href="%s?archive=1&chan_id=%s&start_time=%s&quality=%s" %s>Archive</a>'\
           % (url, chan_id, start_time_str, quality, on_click)

def build_delete_link(chan_id, start_time, url):
    """ Build Delete Link
    @param: chan_id: String: Channel ID
    @param: start_time: String: Program Start Time
    @param: url: String
    """
    start_time_str = '%sZ' % str(start_time).replace(' ', 'T')
    on_click = 'onclick="return confirm(\'Are you sure want to Delete this original MythTV Recording?\');"'
    return '<a href="%s?delete=1&chan_id=%s&start_time=%s" %s>Delete</a>' % (url, chan_id, start_time_str, on_click)

def build_paginate_links(page, url):
    """ Build Paginate Links
    Helper used to build Paginate Links.
    @param: page: Page Number
    @param: url: String
    """
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 0

    previous_page = page - 1 if page > 0 else 0
    next_page = page + 1

    links = '''
    <a href="%s?page=0">First</a>
    <a href="%s?page=%d">Previous</a>
    </td><td><a href="%s?page=%d">Next</a>
    ''' % (url, url, previous_page, url, next_page)

    return page, links

def default_template(content):
    """ Default Template
    @param: content: String: Page Content
    """
    return str('''
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="static/css/table.css">
    </head>
    <body>
    <h2>MythTVArchiveServer</h2>
    <h3><a href="queue">Queue</a> | <a href="recordings">Recordings</a> | <a href="media/" target="blank">Media</a></h3>
    %s
    </body>
    </html>
    ''' % content.encode('utf-8'))