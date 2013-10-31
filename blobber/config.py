# actual size limit is 2KB
METADATA_SIZE_LIMIT = 1950

# file size limit current set to 5MB
FILE_SIZE_LIMIT = 150000000

security_config = {
    # subnets as comma separated string
    'allowed_ips': [
        '10.0.0.0/8',
    ],
    'allowed_filetypes': [
        'zip',
        'etl',
        'dmp',
        'txt',
        'log',
        'gif',
        'jpg', 'jpeg',
        'png',
    ],
}

# files to be Content-Type specific instead of 'downloadable'
blob_mimetypes = {
    'txt': 'text/plain',
    'log': 'text/plain',
    'gif' : 'image/gif',
    'png' : 'image/png',
    'jpeg' : 'image/jpg',
    'jpg' : 'image/jpg',
}
