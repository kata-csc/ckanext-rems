import json
import logging
import re
import itertools

from pylons.i18n import _
import pylons.config as config

import ckan.lib.helpers as h
import ckan.plugins as plugin

import rems_client
import convert

log = logging.getLogger(__name__)


class RemsPlugin(plugin.SingletonPlugin):

    plugin.implements(plugin.IConfigurer, inherit=True)
    plugin.implements(plugin.IPackageController, inherit=True)

    # IConfigurer hooks

    def update_config(self, config):
        plugin.toolkit.add_template_directory(config, "templates")

    # IPackageController hooks

    def create(self, pkg):
        self._update_metadata(pkg)

    def edit(self, pkg):
        self._update_metadata(pkg)

    # Private methods

    def _update_metadata(self, pkg):
        try:
            self._post_metadata(pkg)
        except rems_client.RemsException as e:
            h.flash_notice(
                _('Dataset saved but REMS application creation failed. To '
                  'retry, save dataset later without changes.')
            )
            # TODO: Add failed item to retry queue
            log.debug(str(e))
            log.debug('Adding failed item to retry queue (unimplemented)')

    def _get_pid_subkey(self, pid_str):
        return pid_str.rsplit('_')[-1]

    def _get_pid_index(self, pid_str):
        return pid_str.split('_')[1]


    def _post_metadata(self, pkg):
        '''Push created or updated metadata to REMS.

        :param pkg: package to be committed
        :type pkg: ckan.model.Package object
        :raises rems_client.RemsException: if the primary data PID cannot be retrieved or if connection to REMS fails
        '''

        if (pkg.extras.get('availability') == 'access_application_rems_ida' or
            pkg.extras.get('availability') == 'access_application_rems_other') and \
            not pkg.private:

            log.debug("Posting updated package metadata to Reetta service")

            rems_id = pkg.extras.get('external_id') if pkg.extras.get('availability') == 'access_application_rems_ida' else pkg.id

            if not rems_id:
                raise rems_client.RemsException("Failed to retrieve the ID to send to Reetta service")

            log.debug("Rems ID: {p}".format(p=rems_id))

            # fetch the JSON title string and convert it to format required by REMS
            json_title = json.loads(pkg.title)
            title_list = []
            for k, v in json_title.iteritems():
                # try to convert the 3-letter ISO639-2 T code to two-letter format
                try:
                    l = convert.convert_language_code(k)
                except (ValueError, AttributeError), e:
                    log.warn(str(e))
                    l = k

                title_list.append({'value': v, 'lang': l})

            license_reference = pkg.license_id

            # Use this code if multiple distributors are needed to be placed to rems post request
            # owner_emails = []
            # i = 0
            # while pkg.extras.get('contact_{}_email'.format(str(i))):
            #     owner_emails.append(pkg.extras.get('contact_{}_email'.format(str(i))))
            #     i += 1
            # If the above are uncommented, remove the below line
            owner_emails = [pkg.extras.get('contact_0_email')]
            if not owner_emails:
                raise rems_client.RemsException("Failed to retrieve contact email")

            data_url = pkg.extras.get('access_application_download_URL')

            metadata = rems_client.generate_package_metadata(
                title_list, rems_id, owner_emails, license_reference, data_url)
            metadata_json = json.dumps(metadata)
            # TODO: add 'addCatalogItem' to rabbitMQ queue for asynchronous performance
            request_url = config.get('rems.rest_base_url') + 'addCatalogItem'
            rems_client.post_metadata(request_url, metadata_json, post_format="application/json")

            #return post_success  # Cut from here? So that harvesters don't get flash messages?

            # Note: To be able to update like here, the key must already exist in extras.
            # The validators in ckanext-kata ensure this.
            pkg.extras['access_application_URL'] = rems_client.get_access_application_url(rems_id)


    # def get_data_download_url(self, pkg):
    #     data_url = None
    #     # FIXME: Somehow pick the actual data resource. By resource_type(?):
    #     # 'resources': [{},{...u'resource_type': 'not_known_yet',...},..,{}]
    #     for resource in pkg.resources:
    #         if resource.resource_type == u'documentation':  # FIXME (see above)
    #             data_url = resource.url
    #             break
    #     return data_url