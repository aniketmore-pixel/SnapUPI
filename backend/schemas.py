from pydantic import BaseModel

class GenerateUPIResponse(BaseModel):
    upi: str

class CollectRequest(BaseModel):
    to_upi: str
    amount: float
    merchant: str | None = None

class CollectResponse(BaseModel):
    tx_id: str
    status: str
