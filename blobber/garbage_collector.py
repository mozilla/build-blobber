import time
import os
from sqlalchemy.sql import select, delete, text
from sqlalchemy import create_engine
from sqlalchemy_schema import MetadataBackend
from sqlalchemy.orm import sessionmaker

from blobber.backend import BlobberBackend
from blobber.fs_plugin import FileBackend
from config import dir

# number of seconds in a month of 30-days
month_time = int(2592000)

class GarbageCollector:
    def __init__(self):
        self.table = MetadataBackend.__table__

        cur_path = os.path.dirname(os.path.abspath(__file__))
        self.engine = create_engine("sqlite:////%s/metadata.db" % cur_path)

        self.Session = sessionmaker(bind=self.engine)
        B = BlobberBackend({})
        B.files = FileBackend({"dir": dir})
        self.backend = B

    def connect_to_database(self):
        conn = self.engine.connect()
        return conn

    @property
    def session(self):
        return self.Session()

    def delete_metadata(self):
        conn = self.connect_to_database()

        critical_date = int(time.time()) - month_time
        s = select([self.table]).where("uploadTime<:erase_point")
        result = conn.execute(s, erase_point=critical_date)
        self.hashes = [row for row in result]

        ids = str(tuple([row[0] for row in self.hashes]))
        t = text("DELETE FROM metadata WHERE id in %s;" % ids)
        result = conn.execute(t)

    def delete_data(self):
        hashes = [row[1] for row in self.hashes]
        for h in hashes:
            s = select([self.table]).where("hash=:hash_id")
            results = conn.execute(s, hash_id=h)
            if not results:
                self.backend.delete_blob('sha1', h)

    def run(self):
        self.delete_metadata()
        self.delete_data()

def main():
    gc = GarbageCollector()
    gc.run()

if __name__=="__main__":
    main()
