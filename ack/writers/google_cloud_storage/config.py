from pydantic import BaseModel

from ack.writers.formatters.config import FileFormatEnum


class GoogleCloudStorageWriterConfig(BaseModel):
    bucket: str
    prefix: str = None
    project_id: str
    file_name: str = None
    file_format: FileFormatEnum = FileFormatEnum.njson
