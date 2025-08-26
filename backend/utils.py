import re, random, string, uuid
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")

class Result(Generic[T, E]):
    def __init__(self, ok: bool, value: T | None = None, error: E | None = None):
        self.ok = ok
        self.value = value
        self.error = error

    @staticmethod
    def Ok(v: T):
        return Result(True, value=v)

    @staticmethod
    def Err(e: E):
        return Result(False, error=e)

def generate_upi(name_prefix: str = None):
    banks = ["icici", "hdfcbank", "axis", "sbi", "paytm"]
    prefix = (name_prefix or "user") + ''.join(random.choices(string.digits, k=3))
    return f"{prefix}@{random.choice(banks)}"

UPI_RE = re.compile(r"^[a-zA-Z0-9._-]{3,}@[a-zA-Z0-9._-]{2,}$")
def validate_upi(upi: str) -> Result[str, str]:
    if UPI_RE.match(upi):
        return Result.Ok(upi)
    return Result.Err("Invalid UPI format")
