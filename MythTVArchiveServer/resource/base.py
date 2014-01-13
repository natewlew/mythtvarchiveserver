"""
   :synopsis: Resource Base
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from twisted.web.resource import Resource
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.lib.recordedshows import Recordings


def manage_session(meth):
    """
    Session Manager
    """
    def _session(*args, **kwargs):
        site_registry().init_session()
        ret_val = meth(*args, **kwargs)
        site_registry().close_session()
        return ret_val
    return _session


class BaseDB(Resource):

    def __init__(self):
        Resource.__init__(self)

        self.recordings = Recordings()

    @manage_session
    def render_GET(self, request):
        return self.custom_render(request)

    def custom_render(self, request):
        raise NotImplemented('Need to Implement custom_render')