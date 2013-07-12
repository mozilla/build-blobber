import time
import os
from sqlalchemy.sql import select, delete
from sqlalchemy import create_engine
from sqlalchemy_schema import MetadataBackend

from blobber.backend import BlobberBackend
from blobber.fs_plugin import FileBackend
from config import DIR, METADB_NAME

# number of seconds in a month of 30-days
month_time = int(2592000)

class GarbageCollector:
    def __init__(self):
        self.table = MetadataBackend.__table__

        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.engine = create_engine("sqlite:////%s/%s" % (cur_path, METADB_NAME))

        B = BlobberBackend({})
        B.files = FileBackend({"DIR": DIR})
        self.backend = B

    def connect_to_database(self):
        conn = self.engine.connect()
        return conn

    def delete_metadata(self):
        conn = self.connect_to_database()

        critical_date = int(time.time()) - month_time
        s = select([self.table]).where("uploadTime<:erase_point")
        result = conn.execute(s, erase_point=critical_date)
        self.hashes = [row for row in result]

        ids = [row[0] for row in self.hashes]
        d = self.table.delete().where(self.table.c.id.in_(ids))
        result = conn.execute(d)
        conn.close()

    def delete_data(self):
        conn = self.connect_to_database()
        # FIXME: possible race condition in here between select and delete
        hashes = [row[1] for row in self.hashes]
        for h in hashes:
            s = select([self.table]).where("hash=:hash_id")
            results = conn.execute(s, hash_id=h)
            if not results.fetchone():
                self.backend.delete_blob('sha1', h)
        conn.close()

    def run(self):
        self.delete_metadata()
        self.delete_data()

def main():
    gc = GarbageCollector()
    gc.run()

if __name__=="__main__":
    main()
