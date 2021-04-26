from typing import List, Literal

from pydantic import BaseModel


FORMATS = ("csv", "gz", "njson")


class AmazonS3ReaderConfig(BaseModel):
    bucket: str
    prefix: List[str]
    format: Literal[FORMATS]
    dest_key_split: int = 1
    csv_delimiter: str = ","
    csv_fieldnames: str = None
    region_name: str
    access_key_id: str
    secret_access_key: str
