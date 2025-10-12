import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # e.g. postgresql+psycopg://user:pass@host:5432/db?sslmode=require
    JWT_SECRET = os.getenv("JWT_SECRET","change-me")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN","120"))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL","admin@demo.resto")

settings = Settings()
