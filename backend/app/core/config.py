import os

from dotenv import load_dotenv

load_dotenv()  # reads .env into os.environ so the line below can find these values

DATABASE_URL = (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:5432/{os.environ['POSTGRES_DB']}"
)
