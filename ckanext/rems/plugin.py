import json
import logging
import re

from pylons.i18n import _
import pylons.config as config

import ckan.lib.helpers as h
import ckan.plugins as plugin
import rems_client
import convert

import ckanext.kata.utils as katautils

log = logging.getLogger(__name__)


class RemsPlugin(plugin.SingletonPlugin):

    plugin.implements(plugin.IConfigurer, inherit=True)
    plugin.implements(plugin.IPackageController, inherit=True)

    # IConfigurer hooks

    def update_config(self, config):
        plugin.toolkit.add_template_directory(config, "templates")

    # IPackageController hooks

    def create(self, pkg):
        self._update_metadata(pkg)

    def edit(self, pkg):
        self._update_metadata(pkg)

    # Private methods

    def _update_metadata(self, pkg):
        '''Update REMS metadata

        :param pkg: package to be committed
        :type pkg: ckan.model.Package object
        '''


        pkg_as_dict = pkg.as_dict()
        primary_pids = katautils.get_pids_by_type(
            pid_type="data", data_dict=pkg_as_dict, primary=True, use_id_or_name=True
        )

        if not primary_pids:
            log.error("Could not get primary data PID for package {p}; aborting".format(p=pkg.name))
            return

        data_pid = primary_pids[0]['id']

        self._preprocess_if_ida_dataset(pkg, data_pid)

        if (pkg.extras.get('availability') == u'access_application' and
                pkg.extras['access_application_new_form'] == 'True'):
            log.debug("Posting updated package metadata to REMS")

            titles = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^title', k)])
            langs = sorted([(k,v) for (k,v) in pkg.extras.items() if re.search('^lang_title', k)])
            title_list = []
            for title, lang  in zip(titles, langs):
                title_list.append({'value': title[1], 'lang': lang[1]})
                try:
                    title_list[-1]['lang'] = convert.convert_language_code(lang[1])
                except ValueError, e:
                    log.warn(str(e))

            license_reference = pkg.license_id
            owner_emails = [pkg.extras['contact_0_email']]

            data_url = pkg.extras.get('access_application_download_URL')
            log.debug("access_application_download_URL: %s" % data_url)

            # data_url = None
            # # FIXME: Somehow pick the actual data resource. By resource_type(?):
            # # 'resources': [{},{...u'resource_type': 'not_known_yet',...},..,{}]
            # for resource in pkg.resources:
            #     if resource.resource_type == u'documentation':  # FIXME (see above)
            #         data_url = resource.url
            #         break

            metadata = rems_client.generate_package_metadata(
                title_list, data_pid, owner_emails, license_reference, data_url)
            metadata_json = json.dumps(metadata)
            # TODO: add 'addCatalogItem' to rabbitMQ queue for asynchronous performance
            request_url = config.get('rems.rest_base_url') + 'addCatalogItem'
            post_success = rems_client.post_metadata(
                request_url, metadata_json, post_format="application/json")

            #return post_success  # Cut from here? So that harvesters don't get flash messages?

            if post_success:
                # Note: To be able to update like here, key must exist. Ensured
                # in validators.
                pkg.extras['access_application_URL'] = \
                    rems_client.get_access_application_url(data_pid)
            else:
                h.flash_notice(
                    _('Dataset saved but REMS application creation failed. To '
                      'retry, save dataset later without changes.'))
                # TODO: Add failed item to retry queue
                log.debug('Adding failed item to retry queue (unimplemented)')

    def _preprocess_if_ida_dataset(self, pkg, data_pid):
        '''
        Perform preprocessing specific to IDA datasets if the dataset
        appears to be from the IDA namespace.

        The package object is modified in place.
        '''

        ida_download_url_template = "http://avaa.tdata.fi/remsida/dl.jsp?pid={p}"
        ida_pid_regex = 'urn:nbn:fi:csc-ida\w+'

        if re.match(ida_pid_regex, data_pid):
            url = ida_download_url_template.format(p=data_pid)
            log.info("IDA dataset encountered; assuming download URL to be {u}".format(u=url))
            pkg.extras['access_application_download_URL'] = url
