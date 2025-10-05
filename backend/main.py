import asyncio
import logging
import ssl
import re
import email
import uuid
import base64
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from threading import Thread
# Configuration imports
from config import (
    UPSTREAM_IMAP_HOST,
    UPSTREAM_IMAP_PORT,
    UPSTREAM_IMAP_SSL,
    LISTEN_HOST,
    UNSECURE_PORT,
    SECURE_PORT,
    TLS_CERT_FILE,
    TLS_KEY_FILE,
    QUARANTINE_ENABLED,
    FILTER_MIN_AMOUNT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("imap-proxy")

# =========================
# FastAPI app and models
# =========================
app = FastAPI(title="Email Quarantine Management API", version="1.0.0")
# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent quarantine store (use database in production)
# Structure: { id: { meta, content, status } }
quarantine_store: Dict[str, Dict] = {}

# In-memory accounts store (backed by accounts.json via accounts_api if needed)
# Structure: { id: { email, password, imap_host, imap_port, use_tls, proxy_host, proxy_ports } }
accounts_store: Dict[str, Dict] = {}

class EmailMeta(BaseModel):
    subject: str
    sender: str
    amount: float = 0.0

class EmailContent(BaseModel):
    meta: EmailMeta
    content: str  # base64 encoded email bytes
    status: str = "held"  # held, approved, deleted, delivered

class QuarantinedEmail(BaseModel):
    id: str
    meta: EmailMeta
    content: str
    status: str

# ---- Multi-account models ----
class AccountIn(BaseModel):
    email: str
    password: str
    imap_host: str
    imap_port: int = 993
    use_tls: bool = True
    proxy_host: str = "localhost"
    proxy_unsecure_port: int = 1143
    proxy_secure_port: int = 1993

class Account(AccountIn):
    id: str

# API Endpoints (Quarantine)
@app.get("/quarantine")
async def list_quarantined_emails():
    return {eid: {**data, "id": eid} for eid, data in quarantine_store.items()}

@app.get("/quarantine/{email_id}")
async def get_quarantined_email(email_id: str):
    if email_id not in quarantine_store:
        raise HTTPException(status_code=404, detail="Email not found")
    data = quarantine_store[email_id]
    return {"id": email_id, "meta": data["meta"], "content": data["content"], "status": data["status"]}

@app.post("/quarantine/{email_id}/approve")
async def approve_quarantined_email(email_id: str):
    if email_id not in quarantine_store:
        raise HTTPException(status_code=404, detail="Email not found")
    quarantine_store[email_id]["status"] = "approved"
    return {"id": email_id, **quarantine_store[email_id]}

@app.post("/quarantine/{email_id}/delete")
async def delete_quarantined_email(email_id: str):
    if email_id not in quarantine_store:
        raise HTTPException(status_code=404, detail="Email not found")
    quarantine_store[email_id]["status"] = "deleted"
    return {"id": email_id, **quarantine_store[email_id]}

# =========================
# Multi-account REST Endpoints
# =========================
@app.get("/accounts", response_model=List[Account])
async def list_accounts():
    return [Account(id=aid, **adata) for aid, adata in accounts_store.items()]

@app.post("/accounts", response_model=Account)
async def create_account(account: AccountIn):
    # prevent duplicates by email
    for aid, adata in accounts_store.items():
        if adata.get("email") == account.email:
            raise HTTPException(status_code=409, detail="Account with this email already exists")
    aid = str(uuid.uuid4())
    accounts_store[aid] = account.model_dump()
    logger.info("Created account %s for %s", aid, account.email)
    return Account(id=aid, **accounts_store[aid])

@app.put("/accounts/{account_id}", response_model=Account)
async def update_account(account_id: str, account: AccountIn):
    if account_id not in accounts_store:
        raise HTTPException(status_code=404, detail="Account not found")
    accounts_store[account_id] = account.model_dump()
    logger.info("Updated account %s (%s)", account_id, account.email)
    return Account(id=account_id, **accounts_store[account_id])

@app.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    if account_id not in accounts_store:
        raise HTTPException(status_code=404, detail="Account not found")
    removed = accounts_store.pop(account_id)
    logger.info("Deleted account %s (%s)", account_id, removed.get("email"))
    return {"id": account_id, **removed}

# =========================
# Email filtering utilities
# =========================
amount_pattern = re.compile(r"(?i)(?:amount|total|sum|subtotal|grand total)\D{0,10}(\d+[\.,]\d{2,})")

def extract_meta_and_amount(msg: EmailMessage) -> Tuple[EmailMeta, float]:
    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    body = ""

    # Attempt to get textual content
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    body += part.get_content().strip() + "\n"
                except Exception:
                    pass
    else:
        try:
            body = msg.get_content().strip()
        except Exception:
            body = ""

    # search for amount
    amt = 0.0
    for text in (subject, body):
        for m in amount_pattern.finditer(text or ""):
            try:
                num = m.group(1).replace(",", ".")
                amt = max(amt, float(num))
            except Exception:
                continue

    meta = EmailMeta(subject=subject, sender=sender, amount=amt)
    return meta, amt

def should_quarantine(meta: EmailMeta) -> bool:
    if not QUARANTINE_ENABLED:
        return False
    return meta.amount >= float(FILTER_MIN_AMOUNT)

@dataclass
class ProxyConfig:
    upstream_host: str = UPSTREAM_IMAP_HOST
    upstream_port: int = UPSTREAM_IMAP_PORT
    upstream_ssl: bool = UPSTREAM_IMAP_SSL

# =========================
# IMAP Proxy Session
# =========================
class ImapProxySession:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, config: ProxyConfig):
        self.client_reader = reader
        self.client_writer = writer
        self.config = config
        self.server_reader: Optional[asyncio.StreamReader] = None
        self.server_writer: Optional[asyncio.StreamWriter] = None
        self.alive = True
        self.state = "NONAUTH"  # basic state tracking

    async def connect_upstream(self):
        if self.config.upstream_ssl:
            ssl_ctx = ssl.create_default_context()
            reader, writer = await asyncio.open_connection(self.config.upstream_host, self.config.upstream_port, ssl=ssl_ctx)
        else:
            reader, writer = await asyncio.open_connection(self.config.upstream_host, self.config.upstream_port)
        self.server_reader, self.server_writer = reader, writer
        logger.info("Connected to upstream IMAP %s:%s", self.config.upstream_host, self.config.upstream_port)

    async def relay_server_greeting(self):
        # Relay initial server greeting to client
        greeting = await self.server_reader.readline()
        if greeting:
            self.client_writer.write(greeting)
            await self.client_writer.drain()

    async def read_client_line(self) -> bytes:
        line = await self.client_reader.readline()
        return line

    async def send_to_server(self, data: bytes):
        self.server_writer.write(data)
        await self.server_writer.drain()

    async def send_to_client(self, data: bytes):
        self.client_writer.write(data)
        await self.client_writer.drain()

    async def handle(self):
        try:
            await self.connect_upstream()
            await self.relay_server_greeting()

            # Main loop
            while self.alive:
                line = await self.read_client_line()
                if not line:
                    break

                tag, cmd, rest = self.parse_command(line)
                if cmd == b"APPEND":
                    await self.handle_append(tag, rest)
                elif cmd == b"FETCH":
                    await self.handle_fetch(tag, rest)
                elif cmd == b"LOGOUT":
                    await self.forward_and_relay(line)
                    self.alive = False
                else:
                    await self.forward_and_relay(line)
        except Exception as e:
            logger.exception("Session error: %s", e)
        finally:
            import contextlib
            with contextlib.suppress(Exception):
                if self.server_writer:
                    self.server_writer.close()
                    await self.server_writer.wait_closed()
            with contextlib.suppress(Exception):
                self.client_writer.close()
                await self.client_writer.wait_closed()

    def parse_command(self, line: bytes) -> Tuple[bytes, bytes, bytes]:
        # IMAP:  <command> [args]\r\n
        parts = line.strip().split(b" ", 2)
        if len(parts) == 0:
            return b"", b"", b""
        if len(parts) == 1:
            return parts[0], b"", b""
        if len(parts) == 2:
            return parts[0], parts[1].upper(), b""
        return parts[0], parts[1].upper(), parts[2]

    async def forward_and_relay(self, first_line: bytes):
        # forward first line to server
        await self.send_to_server(first_line)
        # then relay all server responses until tagged completion for this tag
        tag = first_line.split(b" ", 1)[0]
        while True:
            srv = await self.server_reader.readline()
            if not srv:
                break
            await self.send_to_client(srv)
            # tagged completion when a line starts with the tag
            if srv.startswith(tag + b" "):
                break

    async def read_literal(self, rest: bytes) -> Tuple[bytes, bytes]:
        # For commands with literals like APPEND ... {size}\r\n<bytes>
        m = re.search(br"\{(\d+)\}$", rest.strip())
        if not m:
            return rest, b""
        size = int(m.group(1))
        # Read CRLF following the line already consumed by caller
        # Then read literal of size bytes
        literal = await self.client_reader.readexactly(size + 2)
        return rest, literal[:-2]

    async def handle_append(self, tag: bytes, rest: bytes):
        # APPEND mailbox [flags] [date-time] literal
        args, literal = await self.read_literal(rest)
        raw_msg = literal

        try:
            msg: EmailMessage = BytesParser(policy=policy.default).parsebytes(raw_msg)
        except Exception:
            msg = email.message_from_bytes(raw_msg, policy=policy.default)  # type: ignore

        meta, amt = extract_meta_and_amount(msg)

        if should_quarantine(meta):
            qid = str(uuid.uuid4())
            quarantine_store[qid] = {
                "meta": meta.model_dump(),
                "content": base64.b64encode(raw_msg).decode(),
                "status": "held",
            }
            logger.info("Quarantined email %s from %s subject '%s' amount=%.2f", qid, meta.sender, meta.subject, meta.amount)
            # Respond success to client as if APPEND succeeded but do not forward upstream
            ok = b"%b OK APPEND completed (held by proxy)\r\n" % tag
            await self.send_to_client(ok)
        else:
            # forward literal to server
            first = b"%b APPEND %b\r\n" % (tag, args)
            await self.send_to_server(first)
            await self.send_to_server(raw_msg + b"\r\n")
            # relay responses
            await self.relay_until_tag(tag)

    async def relay_until_tag(self, tag: bytes):
        while True:
            srv = await self.server_reader.readline()
            if not srv:
                break
            await self.send_to_client(srv)
            if srv.startswith(tag + b" "):
                break

    async def handle_fetch(self, tag: bytes, rest: bytes):
        # Simple pass-through for FETCH. Could inject flags to indicate quarantine status if desired
        await self.forward_and_relay(b"%b FETCH %b\r\n" % (tag, rest))

# =========================
# Server startup (plain and TLS)
# =========================
import contextlib

async def imap_client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    session = ImapProxySession(reader, writer, ProxyConfig())
    await session.handle()

async def start_imap_server(host: str, port: int, ssl_ctx: Optional[ssl.SSLContext] = None):
    server = await asyncio.start_server(imap_client_handler, host=host, port=port, ssl=ssl_ctx)
    sockets = ", ".join(str(s.getsockname()) for s in server.sockets or [])
    logger.info("IMAP proxy listening on %s", sockets)
    return server

def build_ssl_context(cert_file: str, key_file: str) -> ssl.SSLContext:
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
    return ctx

# =========================
# FastAPI server runner
# =========================

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

async def main_async():
    servers = []
    # Plain server
    servers.append(await start_imap_server(LISTEN_HOST, UNSECURE_PORT, None))
    # TLS server
    try:
        ssl_ctx = build_ssl_context(TLS_CERT_FILE, TLS_KEY_FILE)
        servers.append(await start_imap_server(LISTEN_HOST, SECURE_PORT, ssl_ctx))
    except Exception as e:
        logger.warning("TLS server not started: %s", e)
    # Keep running
    await asyncio.gather(*(s.serve_forever() for s in servers))

def run_imap_proxy_loop():
    asyncio.run(main_async())

# =========================
# Entrypoint combining FastAPI and IMAP proxy
# =========================
if __name__ == "__main__":
    # Run FastAPI in separate thread
    api_thread = Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    # Run IMAP proxy in main thread loop
    run_imap_proxy_loop()
