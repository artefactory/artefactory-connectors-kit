from typing import List, Literal

from pydantic import BaseModel


FORMATS = ("csv", "gz", "njson")


class GoogleCloudStorageReaderConfig(BaseModel):
    bucket: str
    prefix: List[str]
    format: Literal[FORMATS]
    dest_key_split: int = -1
    csv_delimiter: str = ","
    fieldnames: str = None
