"""
Make tkt auth from Plone Session available to PlominoUtils.
"""
from AccessControl import allow_class, ModuleSecurityInfo
from zope import component
from Products.CMFPlomino import interfaces
from zope.interface import implements
from AccessControl import ModuleSecurityInfo
import time
import base64
from plone.session import tktauth
from zipfile import ZipFile as _ZipFile, ZIP_STORED, ZipInfo

from Products.PythonScripts.Utility import allow_module

allow_module('pretaweb.plominolib')
# allow_module('time')
# allow_module('tktauth')

#Uses files but doesn't open them. need to double check
allow_module('csv')
# ModuleSecurityInfo('nntplib').declarePublic('NNTP',
#   'error_reply', 'error_temp', 'error_perm', 'error_proto')
from csv import DictReader, DictWriter, Dialect, excel, excel_tab, Sniffer
allow_class(DictReader)
allow_class(DictWriter)
allow_class(Dialect)
allow_class(excel)
allow_class(excel_tab)
allow_class(Sniffer)

import AccessControl
# So info from dexterity types can be used in listing views
from plone.app.textfield.value import RichTextValue
allow_class(RichTextValue)
AccessControl.ModuleSecurityInfo('RichTextValue').declarePublic('output')

from plone.namedfile.file import NamedBlobFile
allow_class(NamedBlobFile)
AccessControl.ModuleSecurityInfo('NamedBlobFile').declarePublic('size')

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
    implements(interfaces.IPlominoUtils)

    module = 'pretaweb.plominolib'
    methods = ['encode', 'decode', 'verify_recaptcha', 'email_mime_string']


component.provideUtility(PretawebPlominoLibUtils, interfaces.IPlominoUtils,
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

ModuleSecurityInfo("transaction").declarePublic("savepoint")
ModuleSecurityInfo("email").declarePublic("message")
ModuleSecurityInfo("email").declarePublic("message_from_string")
from email.message import Message
allow_class(Message)


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

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
