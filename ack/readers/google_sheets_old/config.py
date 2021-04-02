from typing import List

from pydantic import BaseModel


class GoogleSheetsReaderOldConfig(BaseModel):
    url: str
    worksheet_name: List[str]
