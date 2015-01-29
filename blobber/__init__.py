from .config import blob_mimetypes, security_config


def get_blob_mimetype(filename, default_mimetype):
    """
    Helper function to be used by application when setting the headers.
    Based on the filename extension it determines the mimetype by choosing
    either from predefined mimetypes in config file or from web server granted
    mimetype on request

    """
    extension = filename.split('.')[-1].lower()
    mimetype = blob_mimetypes.get(extension, default_mimetype)
    return mimetype


def filetype_allowed(filename):
    """
    Helper function to determine if a file is allowed to be uploaded on the
    server or not. It runs filename extension against allowed extensions
    specified in the config file.

    """
    extension = filename.split('.')[-1].lower()
    filetype_whitelist = security_config.get('allowed_filetypes', None)
    if extension in filetype_whitelist:
        return True
    return False
