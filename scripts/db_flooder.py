#!/usr/bin/env python
"""Usage: db_flooder.py -u URL...

-u, --url URL          URL to blobber server to upload to. Multiple URLs can be
                       specified, and they will be tried in random order
"""
import os
import time
from blobberc import upload_file
from test_generator import TestGenerator
def main():
    from docopt import docopt
    import poster.streaminghttp
    poster.streaminghttp.register_openers()

    args = docopt(__doc__)

    tGen = TestGenerator(10)
    files = tGen.file_generate()

    for f in files:
            blob_id = upload_file(args['--url'], f, check_first=False)
            print f, blob_id
            time.sleep(5)

if __name__=="__main__":
    main()
