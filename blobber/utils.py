import os
import sys
from IPy import IP
from bottle import parse_auth, request, HTTPError
from functools import wraps

from .config import blob_mimetypes, security_config, \
            USER, PASSWORD


def mkdiropen(filename, mode):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        with ignored(OSError):
            os.makedirs(d)

    return open(filename, mode)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            raise HTTPError(status=401,
                            x_blobber_msg='Authentication required!')
        user, passwd = parse_auth(auth)
        if (user, passwd) != (USER, PASSWORD):
            raise HTTPError(status=403,
                            x_blobber_msg='Authentication failed!')
        return fn(**kwargs)

    return wrapper


def client_allowance(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        if not client_ip or not ip_allowed(client_ip):
            raise HTTPError(status=403,
                        x_blobber_msg='Client IP not allowed to call server!')
        return fn(**kwargs)

    return wrapper


def has_attachment(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = request.files.data
        if not data.file:
            raise HTTPError(status=403,
                            x_blobber_msg='Missing uploaded file!')
        return fn(**kwargs)

    return wrapper


# TODO: TO-REVIEW
def get_blob_mimetype(filename, default_mimetype):
    extension = filename.split('.')[-1].lower()
    mimetype = blob_mimetypes.get(extension, default_mimetype)
    return mimetype


# TODO: TO-REVIEW
def slice_filename(filename_path):
    # filename_path can be any platform-based (OSX, Win, Linux)
    filename_path = os.path.normpath(filename_path)
    return filename_path.split('\\')[-1].split('/')[-1]


# TODO: TO-REVIEW
def filetype_allowed(filename):
    extension = filename.split('.')[-1].lower()
    filetype_whitelist = security_config.get('allowed_filetypes', None)
    if extension in filetype_whitelist:
        return True
    return False


# TODO: TO-REVIEW
def ip_allowed(remote_addr):
    allowed_ips = [IP(i) for i in security_config.get('allowed_ips', None)]
    ip = IP(remote_addr)
    for i in allowed_ips:
        if ip in i:
            return True
    return False
