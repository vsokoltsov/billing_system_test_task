import os

import sqlalchemy
from databases import Database
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app_env = os.environ.get("APP_ENV")
if app_env == "test":
    load_dotenv(os.path.join(BASE_DIR, ".env.test"), verbose=True)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env"))


DATABASE_URL = (
    f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}'\
    f'@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}'\
    f'/{os.environ.get("POSTGRES_DB")}'
)
db = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
