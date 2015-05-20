# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(
    name='ckanext-rems',
    version=version,
    description="Allows using Resource Entitlement Management System (REMS) to"
                " handle access to datasets.",
    long_description="""\
    """,
    classifiers=[],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author=u'CSC – IT Center for Science Ltd.',
    author_email='kata-project@postit.csc.fi',
    url='https://github.com/kata-csc/ckanext-rems',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.rems'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'pycountry >= 1.8',
    ],
    tests_require=[
        'nose',
    ],
        package_data={'ckan': [
        'i18n/*/LC_MESSAGES/*.mo',
        ]
    },
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
        ],
    },
    entry_points=
    '''
    [ckan.plugins]
    rems=ckanext.rems.plugin:RemsPlugin
    [paste.paster_command]
    remscmd = ckanext.rems.rems_command:RemsCommand
    ''',
)
