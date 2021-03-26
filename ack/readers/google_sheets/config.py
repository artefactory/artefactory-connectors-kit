from pydantic import BaseModel


class GoogleSheetsReaderConfig(BaseModel):
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    client_cert: str
    sheet_key: str
    page_number: int = 0
