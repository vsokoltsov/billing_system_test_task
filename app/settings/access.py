import os

APP_HOST = os.environ.get("APP_HOST", "localhost")
APP_PORT = int(os.environ.get("APP_PORT", 8080))
APP_HOME = str(os.environ.get("APP_HOME", "."))
APP_RELOAD = bool(int(os.environ.get("APP_RELOAD", "1")))
BILLING_DB_DSN = os.environ.get("BILLING_DB_DSN", "")
FORCE_ROLLBACK_TRANSACTION = bool(int(os.environ.get("FORCE_ROLLBACK_TRANSACTION", 0)))
