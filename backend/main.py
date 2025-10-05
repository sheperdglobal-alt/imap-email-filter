import asyncio
import logging
import ssl
import re
import email
import aioimaplib
import uuid
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from email import policy
from email.parser import BytesParser
import uvicorn
from threading import Thread

# Configuration imports
from config import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI app
app = FastAPI(title="Email Quarantine Management API", version="1.0.0")

# Persistent quarantine store (use database in production)
quarantine_store: Dict[str, Dict] = {}

class EmailMeta(BaseModel):
    subject: str
    sender: str
    amount: float

class EmailContent(BaseModel):
    meta: EmailMeta
    content: str  # base64 encoded email bytes
    status: str = "held"  # held, approved, deleted, delivered

class QuarantinedEmail(BaseModel):
    id: str
    meta: EmailMeta
    content: str
    status: str

# API Endpoints
@app.get("/quarantine")
async def list_quarantined_emails():
    """List all quarantined emails with metadata"""
    return {eid: {**data, "id": eid} for eid, data in quarantine_store.items()}

@app.get("/quarantine/{email_id}")
async def get_quarantined_email(email_id: str):
    """Get specific quarantined email with full content"""
    if email_id not in quarantine_store:
        raise HTTPException(status_code=404, detail="Email not found")
    
    data = quarantine_store[email_id]
    return {
        "id": email_id,
        "meta": data["meta"],
        "content": data["content"],
        "status": data["status"]
    }
