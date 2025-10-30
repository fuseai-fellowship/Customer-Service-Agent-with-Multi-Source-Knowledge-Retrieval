import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # e.g. postgresql+psycopg://user:pass@host:5432/db?sslmode=require
    JWT_SECRET = os.getenv("JWT_SECRET","change-me")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN","120"))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

    # --- Add ALL these new settings ---
    SMTP_HOST = os.getenv("MAIL_SERVER")
    SMTP_PORT = int(os.getenv("MAIL_PORT", 587))
    SMTP_USER = os.getenv("MAIL_USERNAME")
    SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")
    SMTP_SENDER_EMAIL = os.getenv("MAIL_FROM")
    
    
    SMTP_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() in ("true", "1", "t")
    SMTP_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() in ("true", "1", "t")
    
settings = Settings()
