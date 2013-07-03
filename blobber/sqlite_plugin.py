import sqlite3
import string
import random
import time

class MetadataBackend(object):
    def __init__(self, config):
        self.config = config
        self.create_database()

    def name_generator(self, N=8):
        # return random generated string of size N
        _ = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in range(N))
        return 'metadata_' + _ + '.db'

    def create_database(self):
        try:
            con = sqlite3.connect(self.config['name'])
        except KeyError:
            self.config['name'] = self.name_generator()
            con = sqlite3.connect(self.config['name'])

        sql_command = """CREATE TABLE md (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash VARCHAR(255),
                filename VARCHAR(255),
                filesize VARCHAR(255),
                branch VARCHAR(255),
                mimetype VARCHAR(255),
                uploadTime INTEGER,
                uploadByIp VARCHAR(255));"""

        try:
            con.execute(sql_command)
        except sqlite3.OperationalError, e:
            if e.message == 'table md already exists':
                print 'Table already exists. Moving forward'
                pass
            else:
                raise
        con.close()

    def get_blob_metadata(self, blobhash, filename):
        con = sqlite3.connect(self.config['name'])
        c = con.cursor()
        c.execute("SELECT * FROM md WHERE hash=? AND filename=?",
                  (blobhash, filename))
        result = c.fetchone()
        c.close()
        con.close()

        return result

    def add_blob_metadata(self, blobhash, filename, filesize,
                          branch, mimetype, upload_time, upload_ip):
        con = sqlite3.connect(self.config['name'])
        c = con.cursor()
        c.execute("INSERT INTO md (hash, filename, filesize, branch, mimetype,\
                    uploadTime, uploadByIp) VALUES (?,?,?,?,?,?,?);",
                    (blobhash, filename, filesize, branch,
                     mimetype, upload_time, upload_ip))

        con.commit()
        c.close()
        con.close()

if __name__=="__main__":
    m = MetadataBackend({'name': 'mydatabase.db'})
    m.add_blob_metadata("bcgssdffw", "test.file", "1049814",
                        "test-branch", "application/text",
                        int(time.time()), "192.168.0.1")
    print m.has_blob_metadata("bcgssdffw", "test.file")
