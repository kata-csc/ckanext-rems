import logging
import json

import ckan.plugins as plugin
import rems_client
import settings
import convert

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

    # private methods

    def _update_metadata(self, context, pkg_dict):
        #raise ValueError()  # debugging
        if 'availability' in pkg_dict and pkg_dict['availability'] == u'access_application':
            log.debug("Posting updated package metadata to REMS")

            titles = pkg_dict['langtitle']
            for title in titles:
                try:
                    title['lang'] = convert.convert_language_code(title['lang'])
                except ValueError, e:
                    log.warn(str(e))

            name = pkg_dict['name']
            license_reference = pkg_dict['license_id']
            owner_emails = [ pkg_dict['maintainer_email'] ]

            url = None
            # FIXME: Take url from resource which has: 'resources': [{},{...u'resource_type': 'not_known_yet',...},...,{}]
            if 'resources' in pkg_dict:
                for resource in pkg_dict['resources']:
                    if (resource.has_key('resource_type') and
                        resource['resource_type'] == u'documentation' and  # FIXME (see above)
                        resource['url']):
                        url = resource['url']
                        break

            metadata = rems_client.generate_package_metadata(titles, name, owner_emails, license_reference, url)
            metadata_json = json.dumps(metadata)
            request_url = settings.REMS_REST_BASE_URL + 'addCatalogItem'

            rems_client.post_metadata(request_url, metadata_json, post_format="application/json")
            pkg_dict['access_application_URL'] = rems_client.get_access_application_url(name)
