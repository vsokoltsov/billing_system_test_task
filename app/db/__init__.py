import os

from databases import Database
from dotenv import load_dotenv
import sqlalchemy

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
load_dotenv(os.path.join(BASE_DIR, ".env"))

app_env = os.environ.get('APP_ENV')
DATABASE_URL = f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("POSTGRES_DB")}'
if app_env == 'test':
    db = Database(DATABASE_URL, force_rollback=True)
else:
    db = Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()