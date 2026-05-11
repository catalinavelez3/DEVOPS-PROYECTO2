import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "STATIC_BEARER_TOKEN": "token-super-secreto",
        "SECRET_KEY": "test-secret",
        "JWT_SECRET_KEY": "test-jwt-secret"
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer token-super-secreto",
        "Content-Type": "application/json"
    }


def test_health_returns_200(client):
    response = client.get("/healthzs")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_blacklist_returns_201(client, auth_headers):
    payload = {
        "email": "test@correo.com",
        "app_uuid": str(uuid.uuid4()),
        "blocked_reason": "Fraude detectado"
    }

    response = client.post("/blacklists", json=payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "Email added to blacklist successfully"
    assert body["email"] == "test@correo.com"


def test_get_blacklisted_email_returns_200(client, auth_headers):
    payload = {
        "email": "test@correo.com",
        "app_uuid": str(uuid.uuid4()),
        "blocked_reason": "Fraude detectado"
    }

    client.post("/blacklists", json=payload, headers=auth_headers)
    response = client.get("/blacklists/test@correo.com", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["is_blacklisted"] is True
    assert body["email"] == "test@correo.com"
    assert body["blocked_reason"] == "Fraude detectado"


def test_get_blacklist_without_token_returns_401(client):
    response = client.get("/blacklists/test@correo.com")
    assert response.status_code == 401