import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_USER     = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = os.getenv("DB_NAME", "sensor_db")
    DB_PORT     = int(os.getenv("DB_PORT", "5432"))

    # Flask
    SECRET_KEY  = os.getenv("SECRET_KEY", "change-this-to-a-long-random-string")
    FLASK_ENV   = os.getenv("FLASK_ENV", "production")

    # Google OAuth
    GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Simulator
    MAX_READINGS    = int(os.getenv("MAX_READINGS", "3000"))
    SIMULATOR_DELAY = int(os.getenv("SIMULATOR_DELAY", "5"))   # seconds between readings