import os

DATABASE_URL = os.getenv("DATABASE_URL")
APP_SECRET = os.getenv("APP_SECRET", "secret")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

SCOPES = "https://www.googleapis.com/auth/calendar"
GOOGLE_API_CALENDAR_SERVICE = "calendar"
GOOGLE_API_VERSION = "v3"
ENV = os.getenv("ENVIRONMENT", "development")
PORT = os.getenv("PORT", 5000)

# for dev (not HTTPS) need to set this
if ENV == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

