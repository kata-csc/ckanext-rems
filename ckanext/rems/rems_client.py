"""
Methods for communicating with the Resource Entitlement Management System
"""

import json
import logging
import settings

log = logging.getLogger("ckanext.rems.rems_client")

def generate_json_metadata(pkg_dict):
    metadata = {}
    metadata['titles'] = pkg_dict['langtitle']

    resource = {}
    resource['resourceDomain'] = settings.REMS_RESOURCE_DOMAIN
    resource['resourceId'] = pkg_dict['name']

    if 'resources' in pkg_dict and len(pkg_dict['resources']) > 0:
        resource['resourceUrl'] = pkg_dict['resources'][0]['url']
    metadata['resource'] = resource

    metadata['resource']['owners'] = [ { 'email': pkg_dict['maintainer_email'] } ]

    # FIXME: license metadata

    return json.dumps({ 'simplecatalogitem': metadata })
