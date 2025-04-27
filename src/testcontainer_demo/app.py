import os

import redis
from fastapi import FastAPI, Depends

app = FastAPI()


def get_redis_client() -> redis.Redis:
    """Dependency that returns a Redis client."""
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = os.environ.get("REDIS_PORT", 6379)
    return redis.Redis(host=redis_host, port=int(redis_port), decode_responses=True)


@app.post("/set/{key}/{value}")
def set_key(key: str, value: str, r: redis.Redis = Depends(get_redis_client)):
    r.set(key, value)
    return {"message": f"Key {key} set to {value}"}


@app.get("/get/{key}")
def get_key(key: str, r: redis.Redis = Depends(get_redis_client)):
    value = r.get(key)
    if value is None:
        return {"error": "Key not found"}
    return {"key": key, "value": value}
