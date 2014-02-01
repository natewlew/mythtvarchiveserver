"""
   :synopsis: Setup
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

__version__ = '0.1'
__author__ = 'Nathan Lewis'
__email__ = 'natewlew@gmail.com'
__license__ = 'GPL Version 2'


try:
    import twisted
except ImportError:
    raise SystemExit("twisted not found.  Make sure you "
                     "have installed the Twisted core package.")

#python-sqlalchemy, python-twisted
from setuptools import setup

setup(
    name = "MythTVArchiveServer",
    version = __version__,
    author = __author__,
    author_email = __email__,
    license = __license__,
    packages=['MythTVArchiveServer', 'MythTVArchiveServer.controllers', 'MythTVArchiveServer.lib',
              'MythTVArchiveServer.models', 'MythTVArchiveServer.util', 'MythTVArchiveServer.resource',
              'twisted.plugins',],
    package_data={
            'twisted': ['plugins/mythtvarchiveserver_plugin.py',
                        'plugins/mythtvarchiveserver_media_plugin.py'],
            },
)