"""
Methods for communicating with the Resource Entitlement Management System
"""

import logging

import pylons.config as config
import requests


log = logging.getLogger(__name__)


def generate_package_metadata(titles, id, owner_emails, license_id, url=None):
    '''
    Generates a REMS-compatible metadata structure from the given package metadata.
    The result is a nested structure of dicts and lists that can be readily
    converted to JSON.

    Arguments:
    titles       -- list of {'lang': 'val', 'title': 'val') dicts
    id           -- id of the resource/dataset
    owner_emails -- list of Haka-federated email addresses that identify the owners of the dataset
    license      -- reference of the license used for the dataset
    url          -- (optional) a URL from which the dataset can be obtained
    '''
    catalog_item = {
        'simplecatalogitem': {
            'titles': titles,
            'resource': {
                'resourceDomain': config.get('rems.resource_domain'),
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

    return catalog_item


def generate_license_metadata(licenses, owner_email,
                              resource_domain=None):
    '''
    Generates a REMS-compatible metadata structure for a list of licenses
    ready for importing to REMS. The result is a nested structure of
    dicts and lists that can be readily converted to JSON.

    Arguments:
    licenses        -- a sequence of License objects
    owner_email     -- the email address to be defined as the owner of the licenses in REMS
    resource_domain -- the REMS resource domain for the licenses; if None, use the default set in Pylons configuration
    '''

    if not resource_domain:
        resource_domain = config.get('rems.resource_domain')

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

    :param url:         REMS endpoint URL
    :type url:          str
    :param metadata:    the metadata of a dataset in the JSON or XML format specified by REMS
    :type metadata:     str
    :param post_format: MIME type for the posted data
    :type post_format:  str
    :return:            None
    :raises RemsException: if a connection error occurs or the request returns a non-OK status
    '''

    log.info('Metadata: {md}'.format(md=metadata))
    try:
        resp = requests.post(url,
                             metadata,
                             headers={'Content-Type': post_format},
                             verify=False,  # TODO: Remove in production?
                             cert=(config.get('rems.client_certificate_path'),
                                   config.get('rems.client_private_key_path')))
        if resp.ok:
            rd = resp.json()['Response']
            log.debug('Response status: {st}, code: {co}, message: {msg}'.format(
                st=resp.status_code, co=rd['Code'], msg=rd['Message']))
        else:
            raise RemsException(
                'REMS request failed; Response status: {st}, message: {msg}'.format(
                st=resp.status_code, msg=resp.text)
            )
    except requests.exceptions.ConnectionError, err:
        # TODO: This should retry in background (and notify success)
        # Copied 'except' from ckanext/resourceproxy/controller.py
        log.warn('Could not send metadata because a connection error '
                 'occurred: {er}'.format(er=err))
        raise RemsException(str(err))


def get_access_application_url(resource_id, target="application"):
    '''
    Generates the entry point URL for access application workflow.
    '''
    url = "{base}?target={t}&domain={d}&resource={r}".format(
        base=config.get('rems.access_application_base_url'),
        t=target,
        d=config.get('rems.resource_domain'),
        r=resource_id
    )
    return url


class RemsException(Exception):
    pass
