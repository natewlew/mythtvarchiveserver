"""
   :synopsis: Media Server
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

import os

from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.web.resource import Resource

import MythTVArchiveServer.controllers.registry as registry
from MythTVArchiveServer.controllers.registry import site_registry
from MythTVArchiveServer.resource.queue import QueueResource
from MythTVArchiveServer.resource.recordings import RecordingsResource


registry.init_registry(init_server=False)


class DefaultResource(Resource):
    """
    Default Resource.
    """
    def getChild(self, path, request):
        if path == '':
            return self.getChildWithDefault('queue', request)
        return Resource.getChild(self, path, request)

    def render_GET(self, request):
        return '<html><a href="media/">Media</a></html>'


def media_plugin():

    config = site_registry().config

    static_path = os.path.abspath('../web/static')
    if os.path.exists(static_path) is False:
        static_path = '/usr/share/mythtvarchiveservermedia/web/static'

    media_path = config.archive_directory
    port = config.media_server_port
    root = DefaultResource()
    root.putChild('media', File(media_path, defaultType='video/mpeg'))
    root.putChild('queue', QueueResource())
    root.putChild('recordings', RecordingsResource())
    root.putChild('static', File(static_path))
    reactor.listenTCP(port, Site(root))

    if config.enable_media_server is False:
        reactor.callLater(0.1, reactor.stop)

    reactor.run()

if __name__ == '__main__':
    media_plugin()
