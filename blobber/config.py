# actual size limit is 2KB
METADATA_SIZE_LIMIT = 1950

FILE_SIZE_LIMIT = 400 * 1024 * 1024

security_config = {
    # subnets as comma separated string
    'allowed_ips': [
        '10.0.0.0/8',
        '127.0.0.1/32',
    ],
    'allowed_filetypes': [
        'zip',
        'etl',
        'dmp',
        'txt',
        'log',
        'gif',
        'jpg', 'jpeg',
        'json',
        'png',
        'html',
        'extra',
    ],
}

# files to be Content-Type specific instead of 'downloadable'
blob_mimetypes = {
    'txt': 'text/plain',
    'log': 'text/plain',
    'gif': 'image/gif',
    'png': 'image/png',
    'jpeg': 'image/jpg',
    'jpg': 'image/jpg',
    'json': 'application/json',
    'html': 'text/html',
    'extra': 'text/plain',
}
