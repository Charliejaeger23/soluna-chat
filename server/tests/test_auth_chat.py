
import pytest
from fastapi.testclient import TestClient
from app import app
from db import init_db

init_db()
client = TestClient(app)

def test_register_login_and_send():
    r1 = client.post("/auth/register", json={"username": "alice", "password": "pass"})
    r2 = client.post("/auth/register", json={"username": "bob", "password": "pass"})
    assert r1.status_code == 200
    assert r2.status_code == 200

    t1 = r1.json()["access_token"]
    t2 = r2.json()["access_token"]

    h = client.get("/conversations/bob/history", headers={"Authorization": f"Bearer {t1}"})
    assert h.status_code == 200
    conv_id = h.json()["conversation_id"]

    s = client.post("/conversations/bob/send", json={"content": "hola"}, headers={"Authorization": f"Bearer {t1}"})
    assert s.status_code == 200

    hb = client.get("/conversations/alice/history", headers={"Authorization": f"Bearer {t2}"})
    msgs = hb.json()["messages"]
    assert any(m["content"] == "hola" for m in msgs)
