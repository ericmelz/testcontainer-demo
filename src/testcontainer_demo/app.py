from contextlib import asynccontextmanager
from typing import Optional

import redis
from fastapi import FastAPI

r: Optional[redis.Redis] = None  # This will be initialized at startup


@asynccontextmanager
async def lifespan(_: FastAPI):
    global r
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/set/{key}/{value}")
def set_key(key: str, value: str):
    r.set(key, value)
    return {"message": f"Key {key} set to {value}"}


@app.get("/get/{key}")
def get_key(key: str):
    value = r.get(key)
    if value is None:
        return {"error": "Key not found"}
    return {"key": key, "value": value}
