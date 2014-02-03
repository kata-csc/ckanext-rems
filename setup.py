from setuptools import setup, find_packages
import sys, os

version = '0.1'

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
    author='CSC \xe2\x80\x94 IT Center for Science Ltd.',
    author_email='kata-project@postit.csc.fi',
    url='https://github.com/kata-csc/ckanext-rems',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.rems'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    tests_require=[
        'nose',
    ],
    entry_points=
    '''
    [ckan.plugins]
    rems=ckanext.rems.plugin:RemsPlugin
    ''',
)
