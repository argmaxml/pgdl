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
from time import time
from db_model import get_db, App


class IgnoreHealthCheck(logging.Filter):
    def filter(self, record):
        return "/healthz" not in record.getMessage()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.access")
logger.addFilter(IgnoreHealthCheck())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# route handlers
@app.get("/healthz", tags=["root"])
async def healthz() -> dict:
    return {
        "healthz": "👍"
    }


@app.get("/app/list", tags=["apps"])
async def app_list(db: Session = Depends(get_db)) -> dict:
    apps = db.query(App).all()

    return {
        "data": [app.title for app in apps]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)