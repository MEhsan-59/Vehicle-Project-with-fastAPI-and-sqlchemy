# create_table.py
from database import engine
from models import Base
from logger_setup import logger

Base.metadata.create_all(bind=engine)
logger.info("Tables created successfully.")
print("Tables created successfully.")
