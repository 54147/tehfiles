from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    s3_url: str = "http://localhost:9000"  # local minio s3 url
    s3_access_key: str = "s3_local_access_key"
    s3_secret_key: str = "s3_local_secret_key"
    s3_default_bucket_name: str = "default-bucket"

    allowed_extensions: list[str] = ["txt", "csv", "json"]

    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_username: str = "postgres"
    pg_password: str = "postgres"
    pg_db: str = "db"
    sqlalchemy_echo: bool = True


settings = Settings()