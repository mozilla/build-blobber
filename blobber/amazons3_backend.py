import os
from boto.s3.connection import S3Connection


def upload_to_AmazonS3(hashalgo, blobhash, data_file, headers, metadata):
    """
    When uploading file to Amazon S3 there are two possible scenarios:
    * if file already exists => without uploading the data file, refresh its
        timestamp by changing the object storage method to the same storage
        method it currently has. Because there's no 100% warranty for this
        side effect, we make sure the timestamp has changed by inspecting the
        changes. We uload the file should the side effect fail, overwriting
        old one, thus resetting creation_date.
    * if file doesn't exist => upload it.
    """
    # make sure the bucket name is set within the environment
    BUCKET = os.environ.get(S3_UPLOAD_BUCKET)
    if not BUCKET:
        return

    # open a connection and get the bucket
    conn = S3Connection()
    bucket = conn.get_bucket(BUCKET)

    # get bucket corresponding key for the object
    _key = "blobs/%s/%s/%s" % (metadata['branch'], hashalgo, blobhash)

    key = bucket.get_key(_key)
    with open(data_file, "r") as fd:
        if key:
            # if object exists in bucket then reset storage method
            timestamp = key.last_modified
            key.change_storage_class("STANDARD")

            # make sure the timestamp has been refreshed
            key = bucket.get_key(_key)
            new_timestamp = key.last_modified
            if timestamp == new_timestamp:
                # upload file should refreshing timestamp failed
                key.update_metadata(metadata)
                key.set_contents_from_file(fd, headers=headers)
                key.set_acl('public-read')
            else:
                # update metadata should refreshing timestamp succeeded
                key = bucket.copy_key(key.name, key.bucket.name, key.name,
                                      metadata, preserve_acl=True,
                                      headers=headers)
        else:
            # if object does not exist, upload it
            key = bucket.new_key(_key)
            key.update_metadata(metadata)
            key.set_contents_from_file(fd, headers=headers)
            key.set_acl('public-read')
