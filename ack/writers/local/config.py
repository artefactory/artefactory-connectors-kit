from pydantic import BaseModel

from ack.writers.formatters.config import FileFormatEnum


class LocalWriterConfig(BaseModel):
    directory: str
    file_name: str
    file_format: FileFormatEnum = FileFormatEnum.njson
