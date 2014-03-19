"""
Settings for the Resource Entitlement Management System
extension for CKAN.
"""

REMS_RESOURCE_DOMAIN = "Kata"
REMS_REST_BASE_URL = "https://reetta.csc.fi:8444/rems-rest/"
ACCESS_APPLICATION_BASE_URL = "https://reetta.csc.fi/web/guest/catalogue"

DEFAULT_LICENSE_TYPE = "link"  # possible values: text, attachment, link
CLIENT_PRIVATE_KEY_PATH = '/etc/pki/tls/certs/development.key'
CLIENT_CERTIFICATE_PATH = '/etc/pki/tls/certs/development.crt'