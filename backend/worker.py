import time, random, os, redis, json
from backend_db import SessionLocal
from models import Transaction
from datetime import datetime
import math

REDIS = redis.Redis(host=os.getenv("REDIS_HOST","localhost"), port=int(os.getenv("REDIS_PORT",6379)), decode_responses=True)

# processing config
MAX_RETRIES = 5
BASE_BACKOFF = 1.0  # seconds

def simulate_bank_call(tx):
    # randomly succeed / fail; tune probabilities for tests
    p_success = float(os.getenv("SIM_SUCCESS_PROB", 0.8))
    if random.random() < p_success:
        return True, None
    # sometimes transient error
    if random.random() < 0.5:
        return False, "NETWORK_ERROR"
    return False, "DECLINED"

def process_tx(tx_id):
    # idempotency: check Redis first
    state = REDIS.hgetall(f"tx:{tx_id}")
    if not state:
        # load from DB
        db = SessionLocal()
        tx = db.query(Transaction).filter(Transaction.tx_id==tx_id).first()
        db.close()
        if not tx:
            print("no tx found", tx_id)
            return
        if tx.status != "PENDING":
            return
        attempts = tx.attempt_count
    else:
        attempts = int(state.get("attempts", 0))

    # exponential backoff sleep
    backoff = BASE_BACKOFF * (2 ** attempts)
    time.sleep(backoff)  # simple backoff

    ok, err = simulate_bank_call(tx_id)
    db = SessionLocal()
    tx = db.query(Transaction).filter(Transaction.tx_id==tx_id).first()
    if not tx:
        db.close()
        return

    tx.attempt_count += 1
    if ok:
        tx.status = "SUCCESS"
        tx.last_error = None
        REDIS.hset(f"tx:{tx_id}", mapping={"status":"SUCCESS", "attempts": tx.attempt_count})
        print(f"tx {tx_id} success")
    else:
        tx.last_error = err
        if tx.attempt_count >= MAX_RETRIES:
            tx.status = "FAILED"
            REDIS.hset(f"tx:{tx_id}", mapping={"status":"FAILED", "attempts": tx.attempt_count, "last_error": err})
            print(f"tx {tx_id} failed finally: {err}")
        else:
            tx.status = "PENDING"
            REDIS.hset(f"tx:{tx_id}", mapping={"status":"PENDING", "attempts": tx.attempt_count, "last_error": err})
            # requeue
            REDIS.lpush("pending_txs", tx_id)
            print(f"tx {tx_id} requeued (attempt {tx.attempt_count})")
    db.commit()
    db.close()

def worker_loop():
    print("worker started")
    while True:
        # block pop from pending queue with timeout
        item = REDIS.brpop("pending_txs", timeout=5)  # returns (listname, tx_id) or None
        if not item:
            time.sleep(0.5)
            continue
        _, tx_id = item
        try:
            process_tx(tx_id)
        except Exception as e:
            print("error processing", tx_id, e)
            # requeue safely
            REDIS.lpush("pending_txs", tx_id)
            time.sleep(1)

if __name__ == "__main__":
    worker_loop()
