import settings
import rems_client
import license

import ckan.lib.cli as cli
import ckan.model.license

import sys
import json

class RemsCommand(cli.CkanCommand):
    """
    Usage: remscmd <command> <owner_email> [server_url]

    Allowed commands:

    add_ckan_licenses \t- posts the CKAN license list to REMS

    In all cases, <owner_email> should be a Haka-registered email
    address for the owner of the license or dataset.

    If server_url is not specified, REMS_REST_BASE_URL from settings.py
    will be used.
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(RemsCommand, self).__init__(name)
        self._min_args = 2
        self._max_args = 3

    def command(self):
        self._load_config()

        if len(self.args) < self._min_args or len(self.args) > self._max_args:
            self.parser.print_usage()
            sys.exit(1)

        cmd = self.args[0]
        owner_email = self.args[1]

        if len(self.args) < 3:
            rems_url = None
        else:
            rems_url = self.args[2]

        if cmd == 'add_ckan_licenses':
            self._add_ckan_licenses(rems_url, owner_email)
        else:
            print "Command {c} not recognized".format(c=cmd)

    def _load_config(self):
        super(RemsCommand, self)._load_config()

    def _add_ckan_licenses(self, rems_url, owner_email):
        if rems_url is None:
            rems_url = settings.REMS_REST_BASE_URL + "addLicense"

        license_register = ckan.model.license.LicenseRegister()
        known_licenses = license_register.values()

        licenses = []

        for ckan_license in known_licenses:
            # TODO: support multiple localized versions of licenses?
            lic = license.License(id=ckan_license.id, value_type='link')
            content = license.LicenseLocalizedContent('en', ckan_license.title, ckan_license.url)
            lic.add_localization(content)
            licenses.append(lic)

        metadata = rems_client.generate_license_metadata(licenses, owner_email)
        json_metadata = json.dumps(metadata)

        print "Sending license metadata to {u} ...".format(u=rems_url)
        #print json_metadata
        rems_client.post_metadata(rems_url, json_metadata)

