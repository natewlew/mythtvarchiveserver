"""
   :synopsis: Media Plugin
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from MythTVArchiveServer.mediaserver import media_plugin


class Options(usage.Options):
    optParameters = []


class MyServiceMaker(object):
    """
    Twisted Plugin for the Media Server.
    """
    implements(IServiceMaker, IPlugin)
    tapname = "MythTVArchiveServerMedia"
    description = "MythTVArchiveServer Media Service"
    options = Options

    def makeService(self, options):
        return media_plugin()

serviceMaker = MyServiceMaker()
