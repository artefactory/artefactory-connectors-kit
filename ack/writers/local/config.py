from pydantic import BaseModel
from enum import Enum


class FileFormatEnum(str, Enum):
    njson = "njson"
    zstd = "zstd"


class LocalWriterConfig(BaseModel):
    directory: str
    file_name: str
    file_format: FileFormatEnum = FileFormatEnum.njson
