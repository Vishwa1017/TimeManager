from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import dict_row
import os

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from the .env file.")


connection = Connection.connect(
    DATABASE_URL,
    autocommit=True,
    prepare_threshold=0,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(connection)


checkpointer.setup()