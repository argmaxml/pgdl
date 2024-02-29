from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, Double, String, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from decouple import config
from pathlib import Path
from typing import Dict, List, Optional

__dir__ = Path(__file__).parent.parent.absolute()

# SQLAlchemy configuration
LOCAL_DB = False
try:
    engine = create_engine('postgresql://postgres:argmax@pg:5432/postgres')
except ModuleNotFoundError:
    engine = create_engine('sqlite:///test.db')
    LOCAL_DB = True
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Auction(Base):
    # Represents an auction in the RTB space
    __tablename__ = "auctions"
    eventTimestamp = Column(String, primary_key=True)
    unitDisplayType = Column(String)
    brandName = Column(String)
    bundleId = Column(String)
    countryCode = Column(String)
    deviceId = Column(String)
    osAndVersion = Column(String)
    bidFloorPrice = Column(Double)
    sentPrice = Column(Double)

    # Warm up Q1:
    # How many apps were seen and are running in country = 'US'?

    # Q2: What is the distribution (min, max, Q1, Q3, mean, median) of apps that a given deviceId has
    # Hint: requires groupby, as well as calculating metrics

    # Q3: (need to get for each app its description / category)
    # What is the 2nd most common app category (uses distinct) for users running in:
    # 3a. US
    # 3b. BR
    # 3c. IN
    # Where most common is counted by the amount of the devices each app category holds
    # An example: For US, if "news" apps has 1M devices, and "sports" apps has 0.5M devices (and no other categories for simplicity)
    # then "sports" is the 2nd most common app category in US.
    # Hint: For each app, you need to know under which user it is holded, as well as what is its category
    # Hint#2: Make sure to work on data from the specified geos

class App(Base):
    # App model

    __tablename__ = "apps"
    id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(String)
    ios = Column(Boolean, default=False)
    title = Column(String)
    description = Column(String)
    store_url = Column(String)
    icon = Column(String)
    category_names = Column(String)
    ts = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    def truncate_description(self, max_words=150):
        return ' '.join(self.description.split()[:max_words])


if not LOCAL_DB:
    class AppVector(Base):
        __tablename__ = 'app_vectors'
        id = Column(Integer, primary_key=True)
        bundle_id = Column(String, ForeignKey("apps.bundle_id"))
        content = Column(String)
        embedding = Column(Vector(384))
        clip_embedding = Column(Vector(384)) # ViT-B-16-SigLIP-384



# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def load_pg_extensions():
    if LOCAL_DB:
        return
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS http;'))
        # conn.commit()
    return


if __name__ == "__main__":
    import logging
    import pandas as pd

    logger = logging.Logger("DBFeeder")
    # make logger print to stdout
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    # remove sqlite database
    if (Path(__dir__ / "test.db").exists()):
        logger.info("Found existing SQlite db, removing it")
        Path(__dir__ / "test.db").unlink()
    # create database tables
    Base.metadata.create_all(bind=engine)
    # load extensions
    load_pg_extensions()
    # logger.info("loading Pandas DF of our test_data...")
    # df = pd.read_csv("data/test_data.csv")
    # logger.info("loaded data into Pandas DF")
    # df.to_sql("auctions", engine, if_exists='replace', index=False)
    # logger.info("created table auctions")
    logger.info("Done")