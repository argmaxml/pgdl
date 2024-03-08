from pathlib import Path

__dir__ = Path(__file__).parent.parent.absolute()

from fastapi import FastAPI, Body, Header, Depends, HTTPException, status, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from decouple import config
from uuid import uuid4
from typing import Optional, List, Dict
import json, random, logging
import requests
from time import time
from db_model import get_db, AppVector, SessionLocal
import sentence_transformers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger


class IgnoreHealthCheck(logging.Filter):
    def filter(self, record):
        return "/healthz" not in record.getMessage()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.access")
logger.addFilter(IgnoreHealthCheck())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()
scheduler = AsyncIOScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
text_model = sentence_transformers.SentenceTransformer(config("MODEL_NAME", "BAAI/bge-small-en-v1.5"))

# route handlers
@app.get("/healthz", tags=["root"])
async def healthz() -> dict:
    return {
        "healthz": "👍"
    }

@app.get("/embed", tags=["embed"])
async def embed_text(text: str) -> List[float]:
    lst = text_model.encode([text]).tolist()[0]
    lst =  [round(x, 6) for x in lst]
    return lst


# @app.get("/app/list", tags=["apps"])
# async def app_list(db: Session = Depends(get_db)) -> dict:
#     apps = db.query(App).all()
#     return {
#     "   data": [app.title for app in apps]
#     }

def embed_periodically():
    db = SessionLocal()
    # query app vectors where embedding is null, limit to  16
    app_vectors = db.query(AppVector).filter(AppVector.embedding == None).limit(int(config("BATCH_SIZE", 16))).all()
    if not app_vectors:
        logger.info("No app vectors to embed.")
        return
    # batch the content
    contents = [app_vector.content for app_vector in app_vectors]
    # embed the content
    embeddings = text_model.encode(contents).tolist()
    # embed the content of the app vectors
    for i, app_vector in enumerate(app_vectors):
        app_vector.embedding = embeddings[i]
    db.commit()
    db.flush()
    db.close()

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        embed_periodically,
        trigger=IntervalTrigger(minutes=int(config("EMBED_FREQUENCY", default=1))),
        id="embed_periodically", 
        replace_existing=True,
    )
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)