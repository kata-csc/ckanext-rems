Resource Entitlement Management System (REMS) extension for CKAN. Enables use of REMS access rights management with CKAN datasets.

REMS provides tools to design application forms and workflows for items
requiring authorization. REMS can be used by the end user to apply for access to
a dataset. Users controlling the workflow may use REMS to process the
application and administer previously granted access rights.
See: [https://tnc2013.terena.org/core/presentation/18](https://tnc2013.terena.org/core/presentation/18)

The REMS plugin currently depends on the [Kata extension](https://github.com/kata-csc/ckanext-kata/).

Development
===========

    git clone https://github.com/kata-csc/ckanext-rems.git
    cd ckanext-rems
    # activate virtualenv
    python setup.py develop
    # Add 'rems' for 'ckan.plugins' key in your <development>.ini


Installation
============

You can install ckanext-rems with

    pip install -e git://github.com/kata-csc/ckanext-rems.git#egg=ckanext-rems


.ini configuration
------------------

Put following lines under [app:main]

    rems.resource_domain = Your_domain
    rems.rest_base_url = https://your.rems.host/rest_api/
    rems.access_application_base_url = https://your.rems.host/your_catalogue
    # rems.default_license_type possible values: text, attachment, link
    rems.default_license_type = link
    rems.client_certificate_path = /path/to/development.crt
    rems.client_private_key_path = /path/to/development.key


Shibboleth configuration
------------------------

Configuration notes: config/shibboleth/README.txt
