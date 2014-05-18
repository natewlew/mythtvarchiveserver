"""
   :synopsis: Config Controller
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

import ConfigParser
import os
import json

class ConfigError(Exception):
    pass


class ConfigController(object):

    default_path = '/etc/mythtvarchiveserver/config.cfg'
    path = ''

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()

        self.load_config([os.path.abspath('conf/config.cfg'),
                          os.path.abspath('../conf/config.cfg'),
                          self.default_path])

    def load_config(self, paths):

        for path in paths:
            if os.path.exists(path):
                self.config.read(path)
                self.path = path
                return

        raise ConfigError('Unable to Load Config File')

    def write(self):
        cfg_file = open(self.path,'w')
        self.config.write(cfg_file)
        cfg_file.close()

    @property
    def server_port(self):
        return self.config.getint('archiveserver', 'port')

    @property
    def enable_media_server(self):
        return self.config.getboolean('mediaserver', 'enable')

    @property
    def media_server_port(self):
        return self.config.getint('mediaserver', 'port')

    @property
    def mythtv_server_url(self):
        proto = self.config.get('mythtvserver', 'proto')
        ip = self.config.get('mythtvserver', 'ip')
        backend_port = self.config.getint('mythtvserver', 'backend_port')
        return '%s://%s:%d' % (proto, ip, backend_port)

    @property
    def working_directory(self):
        return self.config.get('files', 'working_dir')

    @property
    def archive_directory(self):
        return self.config.get('files', 'archive_dir')

    @property
    def export_hostname(self):
        return self.config.get('archiveserver', 'export_hostname')

    @property
    def db_dsn(self):
        return 'mysql://%s:%s@%s/%s' % (self.config.get('db', 'user'), self.config.get('db', 'pass'),
                                        self.config.get('db', 'host'), self.config.get('db', 'name'))

    @property
    def db_args(self):
        return (('DBHostName', self.config.get('db', 'host')),
                 ('DBName',    self.config.get('db', 'name')),
                 ('DBUserName',self.config.get('db', 'user')),
                 ('DBPassword',self.config.get('db', 'pass')))

    @property
    def init_db(self):
        return self.config.getboolean('db', 'init')

    @init_db.setter
    def init_db(self, value):
        self.config.set('db', 'init', value)
        self.write()

    @property
    def cleanup_on_error(self):
        return self.config.getboolean('archiveserver', 'cleanup_on_error')

    @property
    def delete_recording_on_finish(self):
        return self.config.getboolean('archiveserver', 'delete_recording_on_finish')

    @property
    def commercial_cut_allowed_error_codes(self):
        try:
            return json.loads(self.config.get('archiveserver', 'commercial_cut_allowed_error_codes'))
        except:
            return []

    @property
    def export_type(self):
        return self.config.get('archiveserver', 'export_type')
