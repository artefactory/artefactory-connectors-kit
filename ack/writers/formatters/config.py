from enum import Enum


class FileFormatEnum(str, Enum):
    njson = "njson"
    zstd = "zstd"