import settings

import ckan.lib.cli as cli
import ckan.model.license

import sys
import json

class RemsCommand(cli.CkanCommand):
    """
    Usage: remscmd <command> <server_url> <owner_email>

    Allowed commands:

    add_ckan_licenses \t- posts the CKAN license list to REMS

    In all cases, <owner_email> should be a Haka-registered email
    address for the owner of the license or dataset.
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(RemsCommand, self).__init__(name)
        self._min_args = 3
        self._max_args = 3

    def command(self):
        self._load_config()

        if len(self.args) < self._min_args or len(self.args) > self._max_args:
            self.parser.print_usage()
            sys.exit(1)

        cmd = self.args[0]
        rems_url = self.args[1]
        owner_email = self.args[2]

        if cmd == 'add_ckan_licenses':
            self._add_ckan_licenses(rems_url, owner_email)
        else:
            print "Command {c} not recognized".format(c=cmd)

    def _load_config(self):
        super(RemsCommand, self)._load_config()

    def _add_ckan_licenses(self, rems_url, owner_email):
        license_register = ckan.model.license.LicenseRegister()
        known_licenses = license_register.values()

        metadata = {}
        metadata['owner'] = { 'email': owner_email }
        metadata['licenses'] = []

        for ckan_license in known_licenses:
            license = {
                'type': settings.LICENSE_TYPE,
                'setreference': ckan_license.id,
                'localizations': [
                    {
                        'lang': 'en',
                        'title': ckan_license.title,
                        'value': ckan_license.url
                    }
                ]
            }

            metadata['licenses'].append(license)

        json_metadata = json.dumps({ 'importlicense': metadata })

        # FIXME: actually send the information
        print json_metadata

