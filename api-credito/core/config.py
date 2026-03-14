import os


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "API Crédito")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    MOCK_BANK_BASE_URL: str = os.getenv("MOCK_BANK_BASE_URL", "http://mock-bank:8001")
    WEBHOOK_CALLBACK_URL: str = os.getenv("WEBHOOK_CALLBACK_URL", "http://api-credito:8000/api/webhooks/bank-callback")

    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")

    SQS_PROPOSALS_QUEUE_NAME: str = os.getenv("SQS_PROPOSALS_QUEUE_NAME", "proposal-processing-queue",)


settings = Settings()