.. contents::

pretaweb.plominolib
===================

Custom Plomino utilities library

Introduction
============

Make tkt auth from Plone Session available to PlominoUtils.

Installation
============

Include ``pretaweb.plominolib`` in the ``eggs`` section of your buildout::

    eggs =
        ...
        pretaweb.plominolib

When this package is present, the ``dataset`` function is available to Plomino formulas. 

Examples::

    # Create constant for secret key and timeout
    secret_key = SECRET_KEY
    timeout = TIMEOUT

    # Encode the email with secret key
    urlsafe_string = encode(secret_key, email)

    # Validate the urlsafe string with secret key and timeout:
    email, is_validate = decode(secret_key, urlsafe_string, timeout)

See plone.session_ for more.

.. _plone.session: https://pypi.python.org/pypi/plone.session
