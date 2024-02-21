from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, text
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
try:
    engine = create_engine('postgresql://postgres:argmax@pg:5432/postgres')
except ModuleNotFoundError:
    engine = create_engine('sqlite:///test.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
        logger.info("Found existsing SQlite db, removing it")
        Path(__dir__ / "test.db").unlink()
    # create database tables
    Base.metadata.create_all(bind=engine)
    # load extensions
    load_pg_extensions()

    logger.info("Done")