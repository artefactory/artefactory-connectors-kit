from pydantic import BaseModel


class LocalWriterConfig(BaseModel):
    directory: str
    file_name: str
