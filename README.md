blobber is a simple server implementing a REST API for uploading files to Amazon S3.

Installation
============
Run `pip install -r requirements.txt` to install Python prerequisites.

Running in development mode
===========================
Run `python application.py` to run a development server. You must specify some required environment variables for proper functioning:

* *CLIENT_USERNAME*, *CLIENT_PASSWORD*: set to a username and password that the client must provide for authentication
* *AWS_ACCESS_KEY_ID*, *AWS_SECRET_ACCESS_KEY*: set to your Amazon access credentials
* *S3_UPLOAD_BUCKET*: set to the Amazon S3 bucket where you would like to store blobs

Running in production mode
==========================
TODO: fill this in

Uploading Files
===============
This server is expected to be used with the [blobuploader] client.

[blobuploader]: https://github.com/mozilla/build-blobuploader
