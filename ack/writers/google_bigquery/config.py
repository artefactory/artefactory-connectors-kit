from typing import Literal

from pydantic import BaseModel


WRITE_DISPOSITIONS = ("truncate", "append")
LOCATIONS = ("EU", "US")


class GoogleBigQueryWriterConfig(BaseModel):
    dataset: str
    project_id: str
    table: str
    bucket: str
    partition_column: str = None
    write_disposition: Literal[WRITE_DISPOSITIONS] = "truncate"
    location: Literal[LOCATIONS] = "EU"
    keep_files: bool = False
