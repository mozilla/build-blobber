S3_BUCKET = "mozilla-releng-blobs"

# actual size limit is 2KB
METADATA_SIZE_LIMIT = 1950

# file size limit current set to 5MB
FILE_SIZE_LIMIT = 5000000

blob_mimetypes = {
    'txt': 'text/plain',
    'log': 'text/plain',
    'gif' : 'image/gif',
    'png' : 'image/png',
    'jpeg' : 'image/jpg',
    'jpg' : 'image/jpg',
}

filetype_whitelist = [
    'dmp',
    'txt',
    'log',
    'gif',
    'jpg', 'jpeg',
    'png',
]
