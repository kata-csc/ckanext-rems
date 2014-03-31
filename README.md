ckanext-rems
============

Resource Entitlement Management System (REMS) extensions for CKAN

Enables using REMS access rights management with CKAN datasets.

REMS provides tools to design application forms and workflows for items
requiring authorization. REMS can be used by end user to apply access rights.
Users controlling workflow may use REMS to administer the application as well as
already granted access rights.
See: [https://tnc2013.terena.org/core/presentation/18](https://tnc2013.terena.org/core/presentation/18)


Develop
=======

    git clone https://github.com/kata-csc/ckanext-rems.git
    cd ckanext-rems
    # activate virtualenv
    python setup.py develop
    # Add 'rems' for 'ckan.plugins' key in your <development>.ini


Installation
============

To install this REMS-plugin

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
