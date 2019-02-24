import os

DATABASE_URL = os.getenv("DATABASE_URL")
APP_SECRET = os.getenv("APP_SECRET", "secret")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

SCOPES = "https://www.googleapis.com/auth/calendar"
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"

# for dev (not HTTPS) need to set this
if os.getenv("ENVIRONMENT", "development") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

