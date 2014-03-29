#!/usr/bin/env python

from setuptools import setup
# from distutils.core import setup

setup(
    name = 'navi',
    packages = ['navi', 'navi.driver', 'navi.proto', 'navi.tools'],
    package_dir = {'navi': 'src/navi',
                   'navi.driver': 'src/navi/driver',
                   'navi.proto': 'src/navi/proto',
                   'navi.tools': 'src/navi/tools',},
    test_suite='test',
    version = '1.0.0',
    description = 'Navi tool for robo',
    author='Pawel Suder',
    author_email = 'pawel@suder.info',
    url = 'http://dev.suder.info/',
    download_url = 'http://github.com/paoolo/navi-python-main/',
    keywords = ['navi', 'hokuyo', 'roboclaw', 'panda', 'amber', 'agh'],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        ],
    long_description = '''\
'''
)
