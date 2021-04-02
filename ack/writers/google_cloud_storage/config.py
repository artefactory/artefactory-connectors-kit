from pydantic import BaseModel


class GoogleCloudStorageWriterConfig(BaseModel):
    bucket: str
    prefix: str = None
    project_id: str
    filename: str = None
