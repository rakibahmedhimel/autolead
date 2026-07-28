from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "")
API_KEY_ENCRYPTION_SECRET = os.getenv("API_KEY_ENCRYPTION_SECRET", "")
SYSTEM_FIRECRAWL_FALLBACK_ENABLED = os.getenv("SYSTEM_FIRECRAWL_FALLBACK_ENABLED", "true").lower() == "true"
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
