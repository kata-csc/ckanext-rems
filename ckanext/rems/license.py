"""
Classes and functions for handling license metadata
and preparing it for sending to REMS.
"""

import pylons.config as config

class License(object):
    """A representation of the metadata of a single license for purposes of the REMS client."""

    def __init__(self, id, value_type=config.get('rems.default_license_type')):
        """
        Arguments:
        id         -- the reference id of the license within the resource domain
        value_type -- how the contents of the license are represented;
                      possible values are 'text', 'attachment' or 'link'

        Also remember to add the contents of the license
        (or a link to it if value_type is 'link' or 'attachment')
        with the add_localization method.
        """

        self.id = id
        self.value_type = value_type
        self.localizations = []

    def add_localization(self, localized_content):
        self.localizations.append(localized_content)

    def as_dict(self):
        self_as_dict = {
            'type': self.value_type,
            'setreference': self.id,
            'localizations': [ loc.as_dict() for loc in self.localizations ]
        }
        return self_as_dict

class LicenseLocalizedContent(object):
    """A representation of the (localized) contents of a single license."""

    def __init__(self, lang, title, content):
        self.lang = lang
        self.title = title
        self.content = content

    def as_dict(self):
        self_as_dict = {
            'lang': self.lang,
            'title': self.title,
            'value': self.content
        }
        return self_as_dict
