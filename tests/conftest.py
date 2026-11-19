"""Fixtures: banco SQLite em memória (StaticPool) isolado por teste + TestClient."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401
from app.db.base import Base  # noqa: E402
from app.db.session import get_db, habilitar_foreign_keys_sqlite  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    habilitar_foreign_keys_sqlite(engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def client(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


CORREGO_PAYLOAD = {
    "nome": "Córrego Ponte Baixa",
    "bairro": "M'Boi Mirim",
    "latitude": -23.6735,
    "longitude": -46.7642,
    "nivelAlertaCm": 120,
    "nivelCriticoCm": 180,
}


@pytest.fixture()
def corrego(client):
    resp = client.post("/api/corregos", json=CORREGO_PAYLOAD)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture()
def sensor(client, corrego):
    resp = client.post("/api/sensores", json={"codigo": "ESP32-PB-01", "corregoId": corrego["id"]})
    assert resp.status_code == 201, resp.text
    return resp.json()


def criar_morador(client, corrego_id, nome="Morador Teste", tipo="NENHUMA", prioritario=False):
    resp = client.post(
        "/api/moradores",
        json={
            "nome": nome,
            "telefone": "(11) 90000-0000",
            "endereco": "Rua Fictícia, 123",
            "corregoId": corrego_id,
            "prioritario": prioritario,
            "tipoNecessidade": tipo,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
