from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, Double, String, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from decouple import config
from pathlib import Path
import csv
from typing import Dict, List, Optional

__dir__ = Path(__file__).parent.parent.absolute()
engine = None

# SQLAlchemy configuration
DB_URL = config("DB_URL", 'postgresql://postgres:argmax@pg:5432/postgres')
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
Base = declarative_base()

class Auction(Base):
    # Represents an auction in the RTB space
    __tablename__ = "auctions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    eventTimestamp = Column(String)
    unitDisplayType = Column(String)
    brandName = Column(String)
    bundleId = Column(String)
    countryCode = Column(String)
    deviceId = Column(String)
    osAndVersion = Column(String)
    bidFloorPrice = Column(Double)
    sentPrice = Column(Double)


class AppVector(Base):
    __tablename__ = 'app_vectors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundleId = Column(String)
    content = Column(String)
    embedding = Column(Vector(int(config("MODEL_DIM", 384))), default=None)



# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def load_pg_extensions():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS http;"))
        conn.commit()
    return

def load_data():
    with open('app_data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            vec = AppVector(bundleId=row['bundleId'], content=row['content'], embedding=None)
            session.add(vec)
    session.commit()


    with open('auctions_data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            auction = Auction(**row)
            session.add(auction)

    session.commit()
    session.close()

if __name__ == "__main__":
    import logging

    logger = logging.Logger("DBFeeder")
    # make logger print to stdout
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    # remove sqlite database
    if (Path(__dir__ / "test.db").exists()):
        logger.info("Found existing SQlite db, removing it")
        Path(__dir__ / "test.db").unlink()
    # load extensions
    load_pg_extensions()
    # create database tables
    Base.metadata.create_all(bind=engine)
    # load data
    logger.info(f"Going to load data to DB")
    load_data()
    logger.info("Done")