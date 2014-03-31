"""
Utility functions for converting metadata values to formats accepted by
the REMS server.
"""

import pycountry
import logging

log = logging.getLogger(__name__)

def convert_language_code(lang_code):
    """
    Convert three-letter ISO 639-2 T language codes to two-letter codes if necessary.
    """

    try:
        pycountry.languages.get(alpha2=lang_code)
        new_lang_code = lang_code
    except KeyError:
        # not already a valid two-letter ISO 639-2 language code -- try converting
        try:
            lang = pycountry.languages.get(terminology=lang_code)
            new_lang_code = lang.alpha2
        except KeyError:
            raise ValueError("Invalid language code: {l}", l=lang_code)

    return new_lang_code
