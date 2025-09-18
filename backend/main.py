from fastapi import FastAPI, HTTPException
from backend_db import init_db, SessionLocal
from models import Transaction
from schemas import GenerateUPIResponse, CollectRequest, CollectResponse
from utils import generate_upi, validate_upi
import uuid, os, redis
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import threading
import time
import json
from fastapi.middleware.cors import CORSMiddleware


# Connect to Redis
REDIS = redis.Redis(host=os.getenv("REDIS_HOST","localhost"), port=int(os.getenv("REDIS_PORT",6379)), decode_responses=True)

app = FastAPI(title="Mini UPI Gateway (sim)")

# CORS setup
origins = [
    "http://localhost:3000",  # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # allow only frontend origin
    allow_credentials=True,
    allow_methods=["*"],         # allow all HTTP methods (GET, POST...)
    allow_headers=["*"],         # allow all headers
)

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/generate_upi", response_model=GenerateUPIResponse)
def api_generate_upi():
    upi = generate_upi()
    return {"upi": upi}

@app.post("/api/collect", response_model=CollectResponse)
def api_collect(req: CollectRequest):
    # validate UPI
    v = validate_upi(req.to_upi)
    if not v.ok:
        raise HTTPException(status_code=400, detail=v.error)

    tx_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        tx = Transaction(tx_id=tx_id, to_upi=req.to_upi, amount=req.amount, status="PENDING")
        db.add(tx)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="tx creation error")
    finally:
        db.close()

    # store quick state in Redis for fast reads and worker pickup
    REDIS.hset(f"tx:{tx_id}", mapping={
        "tx_id": tx_id,
        "to_upi": req.to_upi,
        "amount": req.amount,
        "status": "PENDING",
        "attempts": 0,
        "created_at": datetime.utcnow().isoformat()
    })
    # push onto a pending list queue
    REDIS.lpush("pending_txs", tx_id)

    return {"tx_id": tx_id, "status": "PENDING"}

@app.get("/api/status/{tx_id}")
def api_status(tx_id: str):
    r = REDIS.hgetall(f"tx:{tx_id}")
    if r:
        return r
    # fallback to DB
    db = SessionLocal()
    tx = db.query(Transaction).filter(Transaction.tx_id==tx_id).first()
    db.close()
    if not tx:
        raise HTTPException(status_code=404, detail="tx not found")
    return {
        "tx_id": tx.tx_id,
        "to_upi": tx.to_upi,
        "amount": tx.amount,
        "status": tx.status,
        "attempts": tx.attempt_count,
        "last_error": tx.last_error
    }
    
    
def process_pending_txs():
    while True:
        tx_id = REDIS.rpop("pending_txs")
        if tx_id:
            # simulate processing
            REDIS.hset(f"tx:{tx_id}", "status", "SUCCESS")
        time.sleep(1)

threading.Thread(target=process_pending_txs, daemon=True).start()
