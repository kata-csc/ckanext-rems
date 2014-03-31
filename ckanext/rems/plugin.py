import json
import logging
import re

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
        '''Update REMS metadata

        :param pkg: package to be committed
        :type pkg: ckan.model.Package object
        '''
        if (pkg.extras.get('availability') == u'access_application' and
                pkg.extras['access_application_new_form'] == 'True'):
            log.debug("Posting updated package metadata to REMS")

            titles = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^title', k)])
            langs = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^lang_title', k)])
            title_list = []
            for title, lang  in zip(titles, langs):
                title_list.append({'value': title[1], 'lang': lang[1]})
                try:
                    title_list[-1]['lang'] = convert.convert_language_code(lang[1])
                except ValueError, e:
                    log.warn(str(e))

            name = pkg.name
            license_reference = pkg.license_id
            owner_emails = [pkg.maintainer_email]

            data_url = None
            # FIXME: Somehow pick the actual data resource. By resource_type(?):
            # 'resources': [{},{...u'resource_type': 'not_known_yet',...},..,{}]
            for resource in pkg.resources:
                if resource.resource_type == u'documentation':  # FIXME (see above)
                    data_url = resource.url
                    break

            metadata = rems_client.generate_package_metadata(
                title_list, name, owner_emails, license_reference, data_url)
            metadata_json = json.dumps(metadata)
            # TODO: add 'addCatalogItem' to rabbitMQ queue for asynchronous performance
            request_url = config.get('rems.rest_base_url') + 'addCatalogItem'
            post_success = rems_client.post_metadata(
                request_url, metadata_json, post_format="application/json")

            #return post_success  # Cut from here? So that harvesters don't get flash messages?

            if post_success:
                # Note: To be able to update like here, key must exist. Ensured
                # in validators.
                pkg.extras['access_application_URL'] = \
                    rems_client.get_access_application_url(name)
            else:
                h.flash_notice(
                    _('Dataset saved succesfully but REMS application creation'
                      ' failed. Please edit (w/o changes) & save your dataset'
                      ' later for retry.'))
                # TODO: Add message also to users News feed(?) that REMS application creation failed
                # IDomainObjectModification.notify(self, entity, operation) ??
                # TODO: Add failed item to retry queue
                log.debug('Adding failed item to retry queue (unimplementd)')