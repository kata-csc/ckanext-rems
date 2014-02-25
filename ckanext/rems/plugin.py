import logging

import ckan.plugins as plugin
import rems_client
import settings

log = logging.getLogger("ckanext.rems")


class RemsPlugin(plugin.SingletonPlugin):

    plugin.implements(plugin.IConfigurer, inherit=True)
    plugin.implements(plugin.IPackageController, inherit=True)

    # IConfigurer hooks

    def update_config(self, config):
        plugin.toolkit.add_template_directory(config, "templates")

    # IPackageController hooks

    def after_create(self, context, pkg_dict):
        self._update_metadata(context, pkg_dict)

    def after_update(self, context, pkg_dict):
        self._update_metadata(context, pkg_dict)

    def _update_metadata(self, context, pkg_dict):
        #raise ValueError()  # debugging
        if 'availability' in pkg_dict and pkg_dict['availability'] == u'access_application':
            log.debug("Posting updated package metadata to REMS")
            application_url = pkg_dict['access_application_URL']

            titles = pkg_dict['langtitle']
            name = pkg_dict['name']
            license_reference = pkg_dict['license_id']
            owner_emails = [ pkg_dict['maintainer_email'] ]

            url = None
            if 'resources' in pkg_dict:
                resources = pkg_dict['resources']
                if len(resources) > 0 and 'url' in resources[0]:
                    url = resources['url']

            json = rems_client.package_metadata_to_json(titles, name, owner_emails, license_reference, url)
            request_url = settings.REMS_REST_BASE_URL + 'addCatalogItem'
            rems_client.post_metadata(request_url, json, post_format="application/json")
