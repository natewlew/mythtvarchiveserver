"""
   :synopsis: Setup
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

try:
    import twisted
except ImportError:
    raise SystemExit("twisted not found.  Make sure you "
                     "have installed the Twisted core package.")


#python-sqlalchemy, python-twisted

from setuptools import setup

setup(
    name = "MythTVArchiveServer",
    version = "0.1",
    author = "Nathan Lewis",
    author_email = "natewlew@gmail.com",
    license = "GPL Version 2",
    packages=['MythTVArchiveServer', 'MythTVArchiveServer.controllers', 'MythTVArchiveServer.lib',
              'MythTVArchiveServer.models', 'MythTVArchiveServer.util', 'twisted.plugins',],
    package_data={
            'twisted': ['plugins/mythtvarchiveserver_plugin.py',
                        'plugins/mythtvarchiveserver_media_plugin.py'],
            },
)