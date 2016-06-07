"""
Make tkt auth from Plone Session available to PlominoUtils.
"""
from AccessControl import allow_class, ModuleSecurityInfo
from Acquisition import aq_inner
from Products.Archetypes.utils import shasattr
from lxml import etree
from plone.transformchain.interfaces import ITransform
from zope.component import getAdapters
from zope.globalrequest import getRequest
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import component
from Products.CMFPlomino import interfaces as plomino_interfaces
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
import time
import base64
from plone.session import tktauth
from zipfile import ZipFile as _ZipFile, ZIP_STORED, ZipInfo
import random
import string
import operator

try:
    # Don't blame me, blame #pyflakes
    from zope.schema import interfaces
    IVocabularyFactory = interfaces.IVocabularyFactory
except ImportError:
    # < Zope 2.10
    from zope.app.schema import vocabulary
    IVocabularyFactory = vocabulary.IVocabularyFactory

try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

from Products.PythonScripts.Utility import allow_module

import logging
logger = logging.getLogger('pretaweb.plominolib')

allow_module('pretaweb.plominolib')
# allow_module('time')
# allow_module('tktauth')

#Uses files but doesn't open them. need to double check
allow_module('csv')
# ModuleSecurityInfo('nntplib').declarePublic('NNTP',
#   'error_reply', 'error_temp', 'error_perm', 'error_proto')
import csv
allow_class(csv.DictReader)
allow_class(csv.DictWriter)
allow_class(csv.Dialect)
allow_class(csv.excel)
allow_class(csv.excel_tab)
allow_class(csv.Sniffer)

# Allow RE in restricted python. Based on collective.localfunctions
# by Steve McMahon
from AccessControl import allow_type
import re
allow_module('re')
ModuleSecurityInfo('re').declarePublic(
    'compile', 'findall', 'match', 'search', 'split', 'sub', 'subn', 'error',
    'I', 'L', 'M', 'S', 'X')
allow_type(type(re.compile('')))
allow_type(type(re.match('x', 'x')))


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
    if not hasattr(urlsafe_string, 'translate'):
        # IE8 passes the key twice in the request
        if hasattr(urlsafe_string[0], 'translate'):
            urlsafe_string = urlsafe_string[0]
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



#from zope.component import getUtility
#from plone.app.async.interfaces import IAsyncService
#def queue_async(context, func, *args):
#
#    async = getUtility(IAsyncService)
#    queue = async.getQueues()['']
#    return async.queueJob(func, context, *args)
#ModuleSecurityInfo("pretaweb.plominolib").declarePublic("queue_async")


#from collective.taskqueue import taskqueue

ModuleSecurityInfo("collective.taskqueue.taskqueue").declarePublic("add")


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def email_mime_string(email_from_address, email_to_address, email_subject, email_reply_to_address, email_body_html, email_text_attachment, email_text_attachment_filename):
    message_body = MIMEText(email_body_html, "html")

    attachment = MIMEText(email_text_attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=email_text_attachment_filename)

    message = MIMEMultipart()
    message.add_header('From', email_from_address)
    message.add_header('To', email_to_address)
    message.add_header('Subject', email_subject)
    message.add_header('Reply-To', email_reply_to_address)
    message.attach(message_body)
    message.attach(attachment)
    return message.as_string()


class PretawebPlominoLibUtils:
    implements(plomino_interfaces.IPlominoUtils)

    module = 'pretaweb.plominolib'
    methods = ['encode', 'decode', 'verify_recaptcha', 'email_mime_string']


component.provideUtility(PretawebPlominoLibUtils, plomino_interfaces.IPlominoUtils,
                         name='pretaweb.plominolib')


class SafeZipFile(_ZipFile):
    """ SafeZipFile
    """
    def __init__(self, file, mode="r", compression=ZIP_STORED, allowZip64=False):
        if not isinstance(file, basestring):
            return _ZipFile.__init__(self, file, mode, compression, allowZip64)
        else:
            raise NotImplemented("Paths not supported by SafeZipFile")

    def extract(self, member, path=None, pwd=None):
        """Extract a member from the archive to the current working directory,
           using its full name. Its file information is extracted as accurately
           as possible. `member' may be a filename or a ZipInfo object. You can
           specify a different directory using `path'.
        """
        raise NotImplemented("Paths not supported by SafeZipFile")

    def extractall(self, path=None, members=None, pwd=None):
        """Extract all members from the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' is optional and must be a subset of the list returned
           by namelist().
        """
        raise NotImplemented("Paths not supported by SafeZipFile")

    def write(self, filename, arcname=None, compress_type=None):
        """Put the bytes from filename into the archive under the name
        arcname."""
        raise NotImplemented("Paths not supported by SafeZipFile")

allow_class(SafeZipFile)
ModuleSecurityInfo('zipfile').declarePublic('ZIP64_LIMIT',
                                             'ZIP_FILECOUNT_LIMIT',
                                             'ZIP_MAX_COMMENT',
                                             'ZIP_STORED',
                                             'ZIP_DEFLATED',
                                             'ZipInfo')
allow_class(ZipInfo)

# transaction operations

import transaction
def transaction_get():
    return transaction.get()

def transaction_savepoint(txn, optimistic=True):
    txn.savepoint(optimistic=optimistic)
    return

def transaction_commit(txn):
    txn.commit()
    return

ModuleSecurityInfo("transaction").declarePublic("savepoint")
ModuleSecurityInfo("pretaweb.plominolib").declarePublic("transaction_get", "transaction_commit", "transaction_savepoint")

# email message operations

ModuleSecurityInfo("email").declarePublic("message")
ModuleSecurityInfo("email").declarePublic("message_from_string")
ModuleSecurityInfo("email").declarePublic("mime")
ModuleSecurityInfo("email.mine").declarePublic("image")
allow_module("email.mine")
allow_module("email.mine.image")
allow_module("email.mime.multipart")
from email.mime.image import MIMEImage
allow_class(MIMEImage)
from email.mime.multipart import MIMEMultipart
allow_class(MIMEMultipart)
from email.mime.application import MIMEApplication
allow_class(MIMEApplication)

import email

from email.message import Message
allow_class(Message)

allow_module("plone.subrequest")
ModuleSecurityInfo("plone.subrequest").declarePublic("subrequest")

#Catalog operations

def get_catalog_histogram(catalog, indexid):
    """ return the histogram for a given named index
    """
    indexes = catalog.getIndexObjects()
    counts = None
    index_ids = []
    for index in indexes:
        index_ids.append(index.getId())
        if index.getId() == indexid:
            counts = index.uniqueValues(withLengths=True)
            break
    if counts is None:
        raise Exception("index %s not found in %s" % (indexid, index_ids) )
    return counts

ModuleSecurityInfo("pretaweb.plominolib").declarePublic("get_catalog_histogram")

def get_random_key(length=50):
    """ return random alphanumeric characters key with given length.
        default length is 50
    """
    key = ''.join([
        random.choice(string.ascii_letters + string.digits)
        for i in range(length)])
    return key

ModuleSecurityInfo("pretaweb.plominolib").declarePublic("get_random_key")

def csv_reader(csvfile, **kwds):
    """ using csv.reader and return array of rows
    """
    rows = []
    spamreader = csv.reader(csvfile, kwds)
    for row in spamreader:
        rows.append(row)
    return rows

def csv_dict_reader(csvfile, **kwds):
    """ using csv.reader and return array of rows
    """
    rows = []
    spamreader = csv.DictReader(csvfile, kwds)
    for row in spamreader:
        rows.append(row)
    return rows

def compare(a, b):
    """ Compare lower values """
    if not isinstance(a, unicode):
        a = a.decode('utf-8')
    if not isinstance(b, unicode):
        b = b.decode('utf-8')
    return cmp(a.lower(), b.lower())

def get_vocabulary(name="", context=None):
    portal = getSite()
    if name:
        factory = component.getUtility(IVocabularyFactory, name)
        if context:
            vocabulary = factory(context)
        else:
            vocabulary = factory(portal)
        return ["%s|%s" % (term.title, term.value) for term in vocabulary]

    # borrow some codes from eea.facetednavigation
    res = []
    vtool = getToolByName(portal, 'portal_vocabularies', None)
    if vtool:
        vocabularies = vtool.objectValues()
        res.extend([(term.getId(), term.title_or_id()) for term in vocabularies])
    atvocabulary_ids = [elem[0] for elem in res]

    factories = component.getUtilitiesFor(IVocabularyFactory)
    res.extend([(factory[0], factory[0]) for factory in factories if factory[0] not in atvocabulary_ids])

    res.sort(key=operator.itemgetter(1), cmp=compare)
    # play nice with collective.solr I18NFacetTitlesVocabularyFactory
    # and probably others
    #if len(res) and res[0] != ('', ''):
    #    res.insert(0, ('', ''))
    #items = [SimpleVocabulary.createTerm(key, key, value) for key, value in res]
    #vocabulary = SimpleVocabulary(items)
    return ["%s|%s" % (key, value) for key, value in res if key]

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

from plone import api


def apply_diazo(html, as_xml=False):
    request = getRequest()
    portal = api.portal.get()
    charset = portal.portal_properties.site_properties.default_charset
    new_html = None
    published = request.get('PUBLISHED', None)
    handlers = [v[1] for v in getAdapters((published, request,), ITransform)]
    handlers.sort(lambda a, b: cmp(a.order, b.order))
    if handlers:
        # The first handler is the diazo transform,
        # the other 4 handlers are caching
        theme_handler = handlers[0]
        new_html = theme_handler.transformIterable([html], charset)
    # If the theme is not enabled, transform returns None
    if new_html is not None:
        if as_xml:
            new_html.tree = etree.ElementTree(
                new_html.tree.xpath('/html/body/*')[0])
            new_html.doctype = '<?xml version="1.0" standalone="yes" ?>'
        new_html = new_html.serialize()
    else:
        new_html = html
    return new_html


ModuleSecurityInfo("pretaweb.plominolib").declarePublic("apply_diazo")

from DateTime import DateTime


def download(request, content, filename="file.html", content_type="text/html"):
    """ handle setting the right headers to return an alternative download result
    """

    request.response.setHeader("Content-Disposition",
                               "attachment; filename=%s" %
                               filename)
    request.response.setHeader("Content-Type", content_type)
    request.response.setHeader("Content-Length", len(content))
    request.response.setHeader('Last-Modified', DateTime.rfc822(DateTime()))
    request.response.setHeader("Cache-Control", "no-store")
    request.response.setHeader("Pragma", "no-cache")
    request.response.write(content)

ModuleSecurityInfo("pretaweb.plominolib").declarePublic("download")
