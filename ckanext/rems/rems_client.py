"""
Methods for communicating with the Resource Entitlement Management System
"""

import json

def generate_json_metadata(pkg_dict):
    metadata = {}
    metadata['titles'] = pkg_dict['langtitle']

    resource = {}
    resource['resourceDomain'] = '?'
    resource['resourceId'] = pkg_dict['id']

    if 'resources' in pkg_dict and len(pkg_dict['resources'] > 0):
        resource['resourceUrl'] = pkg_dict['resources'][0]['url']
    metadata['resource'] = resource

    # FIXME: package rest of the metadata

    return json.dumps({ 'simplecatalogitem': metadata })
