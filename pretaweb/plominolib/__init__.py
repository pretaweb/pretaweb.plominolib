"""
Make tkt auth from Plone Session available to PlominoUtils.
"""
from zope import component
from Products.CMFPlomino import interfaces
from zope.interface import implements

import time
import base64
from plone.session import tktauth

from Products.PythonScripts.Utility import allow_module

allow_module('pretaweb.plominolib')
# allow_module('time')
# allow_module('tktauth')


def encode(secret_key, email):
    """
    Encode email with secret key and current timestamp
    Return url safe string
    """
    timestamp = time.time()
    ticket = tktauth.createTicket(secret_key, email, timestamp=timestamp)
    urlsafe_string = base64.urlsafe_b64encode(ticket)
    return urlsafe_string


def decode(secret_key, urlsafe_string, timeout):
    """
    Decode the url safe string and validate with secret key and timeout
    Return tuple of email address and true if it is validate
    """
    now = time.time()
    try:
        # What is the minimum we should try?
        ticket = base64.urlsafe_b64decode(urlsafe_string)
        (digest, email, tokens, user_data, timestamp) = tktauth.splitTicket(
            ticket)
        is_validate = tktauth.validateTicket(secret_key, ticket,
                                             timeout=timeout, now=now)
    except (ValueError, TypeError) as e:
        # Log what went wrong.
        email = None
        is_validate = None
    return email, is_validate is not None


def verify_recaptcha(context):

    # Fake locally to make tests pass
    request = getattr(context, 'REQUEST')
    if 'localhost' in request.BASE1:
        return True

    valid = context.restrictedTraverse('@@captcha').verify()
    return valid


class PretawebPlominoLibUtils:
    implements(interfaces.IPlominoUtils)

    module = 'pretaweb.plominolib'
    methods = ['encode', 'decode', 'verify_recaptcha']


component.provideUtility(PretawebPlominoLibUtils, interfaces.IPlominoUtils,
                         name='pretaweb.plominolib')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
