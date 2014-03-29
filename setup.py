# coding=utf-8
# !/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='navi-python-main',
    packages=['navi', 'navi.driver', 'navi.proto', 'navi.tools', 'navi.tests'],
    package_dir={'navi': 'src/navi',
                 'navi.driver': 'src/navi/driver',
                 'navi.proto': 'src/navi/proto',
                 'navi.tools': 'src/navi/tools',
                 'navi.tests': 'src/navi/tests'},
    install_requires=required,
    version='1.0',
    description='Navi tool for robo in python',
    author=u'Paweł Suder',
    author_email='pawel@suder.info',
    url='http://dev.suder.info/',
    download_url='http://github.com/paoolo/navi-python-main/',
    keywords=['navi', 'hokuyo', 'roboclaw', 'panda'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    long_description='''\
'''
)
