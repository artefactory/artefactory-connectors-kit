from pydantic import BaseModel


class MySQLReaderConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int = 3306
    database: str
    watermark_column: str
    watermark_init: str
    query: str
    query_name: str
    table: str
    redis_state_service_name: str
    redis_state_service_host: str
    redis_state_service_port: int = 6379
