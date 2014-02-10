import logging

import ckan.plugins as plugin
import rems_client

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
            json = rems_client.generate_json_metadata(pkg_dict)
            rems_client.post_metadata(json, post_format="application/json")

