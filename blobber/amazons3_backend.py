from boto.s3.connection import S3Connection

def upload_to_AmazonS3(hashalgo, blobhash, tmpfile, headers):
    fd = open(tmpfile, "r")

    from config import S3_BUCKET

    conn = S3Connection()
    bucket = conn.get_bucket(S3_BUCKET)

    _key = "blobs/%s/%s" % (hashalgo, blobhash)
    key = bucket.new_key(_key)
    key.set_contents_from_file(fd, headers=headers)
    key.set_acl('public-read')

