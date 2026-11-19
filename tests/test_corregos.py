from tests.conftest import CORREGO_PAYLOAD


def test_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_criar_e_listar_corrego_em_camel_case(client, corrego):
    assert corrego["nivelAlertaCm"] == 120
    assert "nivel_alerta_cm" not in corrego
    resp = client.get("/api/corregos")
    assert resp.status_code == 200
    assert [c["id"] for c in resp.json()] == [corrego["id"]]


def test_obter_corrego_inexistente_404(client):
    resp = client.get("/api/corregos/999")
    assert resp.status_code == 404
    assert "não encontrado" in resp.json()["detail"]


def test_criar_corrego_limites_invalidos_422(client):
    payload = {**CORREGO_PAYLOAD, "nivelAlertaCm": 200, "nivelCriticoCm": 100}
    assert client.post("/api/corregos", json=payload).status_code == 422


def test_atualizar_corrego(client, corrego):
    resp = client.put(f"/api/corregos/{corrego['id']}", json={"nome": "Córrego Renomeado"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Córrego Renomeado"
    assert resp.json()["nivelCriticoCm"] == 180


def test_atualizar_corrego_quebrando_limites_422(client, corrego):
    resp = client.put(f"/api/corregos/{corrego['id']}", json={"nivelAlertaCm": 500})
    assert resp.status_code == 422


def test_remover_corrego(client, corrego):
    assert client.delete(f"/api/corregos/{corrego['id']}").status_code == 204
    assert client.get(f"/api/corregos/{corrego['id']}").status_code == 404


def test_status_sem_leituras_normal(client, corrego):
    resp = client.get(f"/api/corregos/{corrego['id']}/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["nivelRisco"] == "NORMAL"
    assert body["ultimaLeitura"] is None


def test_status_reflete_ultima_leitura(client, sensor, corrego):
    client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 50, "chuvaMmHora": 0})
    client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 95, "chuvaMmHora": 10})
    body = client.get(f"/api/corregos/{corrego['id']}/status").json()
    assert body["nivelAguaCm"] == 95
    assert body["nivelRisco"] == "ATENCAO"
    assert body["ultimaLeitura"]["nivelAguaCm"] == 95


def test_sensor_codigo_duplicado_409(client, sensor, corrego):
    resp = client.post("/api/sensores", json={"codigo": sensor["codigo"], "corregoId": corrego["id"]})
    assert resp.status_code == 409


def test_sensor_corrego_inexistente_404(client):
    resp = client.post("/api/sensores", json={"codigo": "ESP32-XX-01", "corregoId": 999})
    assert resp.status_code == 404
