"""
Methods for communicating with the Resource Entitlement Management System
"""

import json
import logging

import requests

import ckan.lib.base as base
import settings

log = logging.getLogger("ckanext.rems.rems_client")


def package_metadata_to_json(titles, id, owner_emails, license, url=None):
    '''
    Generates a REMS-compatible JSON dump from the given package metadata.

    Arguments:
    titles       -- list of (lang, title) tuples
    id           -- id of the resource/dataset
    owner_emails -- list of Haka-federated email addresses that identify the owners of the dataset
    license      -- reference of the license used for the dataset
    url          -- (optional) a URL from which the dataset can be obtained
    '''
    metadata = {
        'titles': titles,
        'resource': {
            'resourceDomain': settings.REMS_RESOURCE_DOMAIN,
            'resourceId': id,
            'owners': [
                {'email': email } for email in owner_emails
            ]
        },
        'licenses': [
            {
                'reference': license
            }
        ]
    }
    if url:
        metadata['resource']['resourceUrl'] = url

    # TODO: check for non-emptiness of owners list?

    return json.dumps({ 'simplecatalogitem': metadata })


def post_metadata(url, metadata, post_format="application/json"):
    '''
    Post catalog item (metadata of a dataset) or a license reference to REMS.

    DEV: Email for 'ktester' account is 'kata.tester@funet.fi'
    '''
    # TODO: Because of key handling, should this be private function? Add security?
    log.info('Metadata: {md}'.format(md=metadata))
    try:
        resp = requests.post(url,
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
