from pydantic import BaseModel

from ack.writers.formatters.config import FileFormatEnum


class AmazonS3WriterConfig(BaseModel):
    bucket_name: str
    bucket_region: str
    access_key_id: str
    access_key_secret: str
    prefix: str = None
    filename: str
    fileformat: FileFormatEnum = FileFormatEnum.njson
