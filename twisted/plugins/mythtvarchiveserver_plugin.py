"""
   :synopsis: Archive Plugin
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from MythTVArchiveServer.server import twistd_plugin


class Options(usage.Options):
    optParameters = []


class MyServiceMaker(object):
    """
    Twisted Plugin for the Archive Server.
    """
    implements(IServiceMaker, IPlugin)
    tapname = "MythTVArchiveServer"
    description = "Server to Transcode and Archive Mythtv recordings"
    options = Options

    def makeService(self, options):
        return twistd_plugin()

serviceMaker = MyServiceMaker()
