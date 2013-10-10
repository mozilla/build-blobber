from .config import blob_mimetypes, security_config

def get_blob_mimetype(filename, default_mimetype):
    extension = filename.split('.')[-1].lower()
    mimetype = blob_mimetypes.get(extension, default_mimetype)
    return mimetype


def filetype_allowed(filename):
    extension = filename.split('.')[-1].lower()
    filetype_whitelist = security_config.get('allowed_filetypes', None)
    if extension in filetype_whitelist:
        return True
    return False
