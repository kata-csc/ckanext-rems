"""
Methods for communicating with the Resource Entitlement Management System
"""

import json
import logging

import requests

import ckan.lib.base as base
import settings

log = logging.getLogger("ckanext.rems.rems_client")

def generate_json_metadata(pkg_dict):
    metadata = {}
    metadata['titles'] = pkg_dict['langtitle']

    resource = {}
    resource['resourceDomain'] = settings.REMS_RESOURCE_DOMAIN
    resource['resourceId'] = pkg_dict['name']

    if 'resources' in pkg_dict and len(pkg_dict['resources']) > 0:
        # resource['resourceUrl'] = pkg_dict['resources'][0]['url']  # This gives error, no 'url' in resource
        resource['resourceUrl'] = pkg_dict['access_application_URL']
    metadata['resource'] = resource

    metadata['resource']['owners'] = [ { 'email': pkg_dict['maintainer_email'] } ]

    # FIXME: license metadata

    return json.dumps({ 'simplecatalogitem': metadata })

def post_metadata(metadata, post_format="application/json"):
    '''
    Post catalog item (metadata of a dataset) to REMS.

    DEV: Email for 'ktester' account is 'kata.tester@funet.fi'
    '''
    # TODO: Because of key handling, should this be private function? Add security?
    log.info('Metadata: {md}'.format(md=metadata))
    request_url = settings.REMS_REST_BASE_URL + 'addCatalogItem'
    try:
        resp = requests.post(request_url,
                             metadata,
                             headers={'Content-Type': post_format},
                             verify=False,  # TODO: Remove in production?
                             cert=(settings.CLIENT_CERTIFICATE_PATH,
                                   settings.CLIENT_PRIVATE_KEY_PATH))
        rd = resp.json()['Response']
        log.debug('Response status: {st}, code: {co}, message: {msg}'.format(
            st=resp.status_code, co=rd['Code'], msg=rd['Message']))
        return resp.ok  # True
    # FIXME: Copied 'except' from ckanext/resourceproxy/controller.py
    except requests.exceptions.ConnectionError, error:
        details = '''Could not send metadata because a
                            connection error occurred. %s''' % error
        base.abort(500, detail=details)
