"""
Methods for communicating with the Resource Entitlement Management System
"""

import logging

import requests

import ckan.lib.base as base
import settings

log = logging.getLogger("ckanext.rems.rems_client")


def generate_package_metadata(titles, id, owner_emails, license_id, url=None):
    '''
    Generates a REMS-compatible metadata structure from the given package metadata.
    The result is a nested structure of dicts and lists that can be readily
    converted to JSON.

    Arguments:
    titles       -- list of (lang, title) tuples
    id           -- id of the resource/dataset
    owner_emails -- list of Haka-federated email addresses that identify the owners of the dataset
    license      -- reference of the license used for the dataset
    url          -- (optional) a URL from which the dataset can be obtained
    '''
    catalog_item = {
        'simplecatalogitem': {
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
                    'reference': license_id
                }
            ]
        }
    }
    if url:
        catalog_item['simplecatalogitem']['resource']['resourceUrl'] = url

    # TODO: check for non-emptiness of owners list?

    return catalog_item


def generate_license_metadata(licenses, owner_email, resource_domain=settings.REMS_RESOURCE_DOMAIN):
    '''
    Generates a REMS-compatible metadata structure for a list of licenses
    ready for importing to REMS. The result is a nested structure of
    dicts and lists that can be readily converted to JSON.

    Arguments:
    licenses        -- a sequence of License objects
    owner_email     -- the email address to be defined as the owner of the licenses in REMS
    resource_domain -- the REMS resource domain for the licenses
    '''

    licenses_dict = {
        'importlicense': {
            'resourcedomain': resource_domain,
            'owner': {
                'email': owner_email
            },
            'licenses': [ l.as_dict() for l in licenses ]
        }
    }

    return licenses_dict


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
        rd = resp.json['Response']
        log.debug('Response status: {st}, code: {co}, message: {msg}'.format(
            st=resp.status_code, co=rd['Code'], msg=rd['Message']))
        return resp.ok  # True
    # FIXME: Copied 'except' from ckanext/resourceproxy/controller.py
    except requests.exceptions.ConnectionError, error:
        details = '''Could not send metadata because a
                            connection error occurred. %s''' % error
        base.abort(500, detail=details)


def get_access_application_url(resource_id, target="application"):
    '''
    Generates the entry point URL for access application workflow.
    '''
    url = "{base}?target={t}&domain={d}&resource={r}".format(
        base=settings.ACCESS_APPLICATION_BASE_URL,
        t=target,
        d=settings.REMS_RESOURCE_DOMAIN,
        r=resource_id
    )
    return url
