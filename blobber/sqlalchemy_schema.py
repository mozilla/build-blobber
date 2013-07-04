from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MetadataBackend(Base):
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True)
    hash = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    filesize = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=False)
    mimetype = Column(String(255), nullable=False)
    uploadTime = Column(Integer, nullable=False)
    uploadByIp = Column(String(255), nullable=False)

    def __init__(self, blobhash, filename, filesize, branch,
                 mimetype, upload_time, upload_ip):
        self.hash = blobhash
        self.filename = filename
        self.filesize = filesize
        self.branch = branch
        self.mimetype = mimetype
        self.uploadTime = upload_time
        self.uploadByIp = upload_ip
