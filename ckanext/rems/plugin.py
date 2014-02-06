import logging

import rems_client

from ckan.plugins import SingletonPlugin
from ckan.plugins import implements
from ckan.plugins import toolkit
from ckan.plugins import IConfigurer, IPackageController

log = logging.getLogger("ckanext.rems")

class RemsPlugin(SingletonPlugin):

    implements(IConfigurer, inherit=True)
    implements(IPackageController, inherit=True)

    # IConfigurer hooks

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")

    # IPackageController hooks

    def after_create(self, context, pkg_dict):
        self._update_metadata(context, pkg_dict)

    def after_update(self, context, pkg_dict):
        self._update_metadata(context, pkg_dict)

    def _update_metadata(self, context, pkg_dict):
        #raise ValueError()  # debugging
        if 'availability' in pkg_dict and pkg_dict['availability'] == u'access_application':
            application_url = pkg_dict['access_application_URL']
            json = rems_client.generate_json_metadata(pkg_dict)

            # TODO: post metadata