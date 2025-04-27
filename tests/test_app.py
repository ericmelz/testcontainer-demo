import os

import pytest
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="module")
def redis_container():
    """Start a real Redis container before tests and stop it after."""
    with RedisContainer(port=6379) as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)

        # Set environment vars for the app if needed
        os.environ["REDIS_HOST"] = host
        os.environ["REDIS_PORT"] = str(port)

        yield host, port


@pytest.fixture(scope="module")
def app(redis_container):
    """Override the FastAPI app's Redis connection."""
    from testcontainer_demo.app import app as fastapi_app
    import redis

    host, port = redis_container
    new_redis = redis.Redis(host=host, port=int(port), decode_responses=True)

    # update the global r variable
    global r
    fastapi_app.r = new_redis

    # Also update the module-level r
    import testcontainer_demo.app
    testcontainer_demo.app.r = new_redis

    return fastapi_app


@pytest.fixture(scope="module")
def client(app):
    """FastAPI test client."""
    return TestClient(app)


def test_set_and_get_key(client):
    response = client.post("/set/foo/bar")
    assert response.status_code == 200
    assert response.json() == {"message": "Key foo set to bar"}

    response = client.get("/get/foo")
    assert response.status_code == 200
    assert response.json() == {"key": "foo", "value": "bar"}


def test_missing_key(client):
    response = client.get("/get/missing")
    assert response.status_code == 200
    assert response.json() == {"error": "Key not found"}
