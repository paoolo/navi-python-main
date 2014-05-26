import ConfigParser
import os
import sys

__author__ = 'paoolo'


class Config(object):
    def __init__(self, *args):
        self.__config = ConfigParser.ConfigParser()
        self.add_config_ini(*args)

    def __getattr__(self, name):
        # noinspection PyBroadException
        try:
            return self.__config.get('default', name)
        except Exception as n_exp:
            print 'Cannot found value for %s in config' % name
            return None

    def add_config_ini(self, *args):
        map(lambda config_file_path: self.__config.read(config_file_path), args)


pwd = os.path.dirname(os.path.abspath(__file__))
sys.modules[__name__] = Config('%s/config.ini' % pwd)


def add_config_ini(*args):
    sys.modules[__name__].add_config_ini(*args)