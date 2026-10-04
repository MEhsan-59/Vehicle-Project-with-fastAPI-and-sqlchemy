# database.py
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from logger_setup import logger

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.critical("DATABASE_URL is not set. Check your .env file.")
    raise ValueError("DATABASE_URL environment variable is not set.")

is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_conn, _record):
        dbapi_conn.execute("PRAGMA foreign_keys = ON")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("Database engine initialized successfully.")


def get_db():
    db = SessionLocal()
    logger.debug("Database session opened.")
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")
