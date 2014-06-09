import ConfigParser
import os
import sys

__author__ = 'paoolo'


class Config(object):
    def __init__(self, *args):
        self.__values = {}
        self.__config = ConfigParser.ConfigParser()
        self.add_config_ini(*args)

    def __getattr__(self, name):
        # noinspection PyBroadException
        try:
            if name not in self.__values:
                value = self.__config.get('default', name)
                self.__values[name] = value
            return self.__values[name]
        except Exception as _:
            print 'Cannot found value for %s in config' % name
            return None

    def add_config_ini(self, *args):
        map(lambda config_file_path: self.__config.read(config_file_path), args)

    def set(self, key, value):
        self.__values[key] = value

    def get_all(self):
        return self.__values


pwd = os.path.dirname(os.path.abspath(__file__))
sys.modules[__name__] = Config('%s/config.ini' % pwd)


def add_config_ini(*args):
    sys.modules[__name__].add_config_ini(*args)


def set(key, value):
    sys.modules[__name__].set(key, value)


def get_all():
    sys.modules[__name__].get_all()