import os

import databases
import sqlalchemy

DATABASE_URL = os.environ.get("DUNDERCHAN_SQL_URL", "sqlite:///./test.db")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

poasts = sqlalchemy.Table(
    "poasts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("reply_to", sqlalchemy.Integer, nullable=True),
)

metadata.create_all(engine)
