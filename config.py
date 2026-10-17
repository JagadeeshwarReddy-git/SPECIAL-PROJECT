import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AI Social Media Analytics"
APP_VERSION = "2.0"

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

DATABASE_NAME = "analysis.db"
MAX_COMMENTS = 1000