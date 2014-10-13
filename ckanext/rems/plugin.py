import json
import logging
import re

from pylons.i18n import _
import pylons.config as config

import ckan.lib.helpers as h
import ckan.plugins as plugin
import ckan.model as model
from ckan.lib.base import c
from ckan.logic import get_action

import rems_client
import convert

import ckanext.kata.utils as katautils

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
            log.debug('Adding failed item to retry queue (unimplemented)')


    def _post_metadata(self, pkg):
        '''Push created or updated metadata to REMS.

        :param pkg: package to be committed
        :type pkg: ckan.model.Package object
        :raises rems_client.RemsException: if the primary data PID cannot be retrieved or if connection to REMS fails
        '''

        if (pkg.extras.get('availability') == u'access_application' and
                pkg.extras['access_application_new_form'] == 'True'):
            log.debug("Posting updated package metadata to REMS")

            # Some data dict juggling is needed in order to get the primary data PID consistently
            tmp_context = {'model': model, 'session': model.Session, 'user': c.user}
            tmp_data_dict = {'id': pkg.id}
            data_dict = get_action('package_show')(tmp_context, tmp_data_dict)

            primary_pid = katautils.get_primary_pid(pid_type='data', data_dict=data_dict)

            if not primary_pid:
                raise rems_client.RemsException("Failed to retrieve primary data PID")

            titles = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^title', k)])
            langs = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^lang_title', k)])
            title_list = []
            for title, lang  in zip(titles, langs):
                title_list.append({'value': title[1], 'lang': lang[1]})
                try:
                    title_list[-1]['lang'] = convert.convert_language_code(lang[1])
                except ValueError, e:
                    log.warn(str(e))

            license_reference = pkg.license_id
            owner_emails = [pkg.extras['contact_0_email']]

            data_url = pkg.extras.get('access_application_download_URL')

            metadata = rems_client.generate_package_metadata(
                title_list, primary_pid, owner_emails, license_reference, data_url)
            metadata_json = json.dumps(metadata)
            # TODO: add 'addCatalogItem' to rabbitMQ queue for asynchronous performance
            request_url = config.get('rems.rest_base_url') + 'addCatalogItem'
            rems_client.post_metadata(request_url, metadata_json, post_format="application/json")

            #return post_success  # Cut from here? So that harvesters don't get flash messages?

            # Note: To be able to update like here, the key must already exist in extras.
            # The validators in ckanext-kata ensure this.
            pkg.extras['access_application_URL'] = rems_client.get_access_application_url(primary_pid)


    # def get_data_download_url(self, pkg):
    #     data_url = None
    #     # FIXME: Somehow pick the actual data resource. By resource_type(?):
    #     # 'resources': [{},{...u'resource_type': 'not_known_yet',...},..,{}]
    #     for resource in pkg.resources:
    #         if resource.resource_type == u'documentation':  # FIXME (see above)
    #             data_url = resource.url
    #             break
    #     return data_url