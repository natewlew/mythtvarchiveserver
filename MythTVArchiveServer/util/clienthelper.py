"""
   :synopsis: Client Helper
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from xmlrpclib import Server


def archive_recording(server_url, chan_id, start_time, quality):
    """ Archive Recording
    Helper function used call the xmlrpc server and archive a recording.
    """
    try:
        s = Server(server_url)
        result = s.archive(chan_id, start_time, quality)
    except Exception, e:
        response = 'Error Archiving Recording: %r' % e
    else:
        if result.get('success', False) is True:
            response = result.get('message', '')
        else:
            response = 'Failed to Archive Recording: %s' % result.get('message', '')
    return response