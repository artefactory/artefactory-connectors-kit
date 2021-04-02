from pydantic import BaseModel


class AmazonS3WriterConfig(BaseModel):
    bucket_name: str
    bucket_region: str
    access_key_id: str
    access_key_secret: str
    prefix: str = None
    filename: str
