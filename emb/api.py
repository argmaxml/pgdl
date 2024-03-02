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
import pandas as pd
import json, random, logging
import requests
from time import time
from db_model import get_db
import sentence_transformers
# from PIL import Image
# from transformers import CLIPProcessor, CLIPModel
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
text_model = sentence_transformers.SentenceTransformer('BAAI/bge-base-en-v1.5')

# route handlers
@app.get("/healthz", tags=["root"])
async def healthz() -> dict:
    return {
        "healthz": "👍"
    }

@app.get("/embed/text", tags=["embed"])
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

def my_periodic_task():
    print("Performing a periodic task every 5 minutes.")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        my_periodic_task,
        trigger=IntervalTrigger(minutes=5),
        id="my_periodic_task",  # ID for this job
        replace_existing=True,
    )
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)